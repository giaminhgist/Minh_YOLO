# Run Experiment

When this resource is used: when the user says "run experiment", "deploy to server", "launch this training job", or the execution stage of an approved experiment plan is reached.

Deploy and run ML experiment: $ARGUMENTS

## Step 0: Cost and Authorization Gate (always first)

Compute is money and someone else's time. Before touching any remote machine or provider:

- **Never auto-spend.** Launching a paid/rented resource (cloud GPU, serverless GPU, spot instance) requires the user's explicit approval of the provider, the instance/GPU type, and a budget cap. No implicit approval from an earlier similar run.
- **Never auto-provision.** This resource does not rent machines on its own. If no compute is configured, stop and ask the user rather than picking a provider.
- **Report the running cost** of any rented resource while it is alive, and state the projected total before launch.
- **Honest capability gate.** There is no bundled serverless-GPU or cloud-provisioning tool here: if the user's intended backend has no configured CLI, credentials, or SSH entry, the correct outcome is "compute backend unavailable — configure it or run locally", not an improvised one.
- **No cross-model reviewer is invoked by this resource.** Nothing here produces a verdict about results; do not claim any external validation of a run.

## Step 1: Detect Environment

Read the project's `CLAUDE.md` to determine the experiment environment:

- **Local GPU** (`gpu: local`): look for local CUDA/MPS setup info
- **Remote server** (`gpu: remote`): look for SSH alias, conda env, code directory
- **Rented instance** (`gpu: rented`): an already-running paid instance the user has approved and recorded (e.g. an instances file at project root with host, port, hourly cost, and `max_budget`). Treat it as a remote SSH host plus an active billing meter. If the instances file has no running entry, stop at Step 0 and ask — do not create one.
- **No configuration found**: ask the user. Do not guess, and do not silently default to a cloud provider.

**Environment contract** (`references/compute-env-contract.md`): before building or
trusting any environment, read the provider's env ledger (project-local, e.g.
`.minh-agent/compute/<provider>.md` or the project's existing server-notes file) — an
unchanged spec hash means warm-reuse, a changed one means rebuild. New env -> write the
declarative spec first, render it for this provider's shape, and never declare it ready on
import-success alone: run the seeded kernel witness, and after any rebuild/doc edit run the
agent-follows-doc pass (a fresh subagent executes the documented invocation verbatim and
reports doc-vs-reality divergence).

### Step 2: Pre-flight Check

Check GPU availability on the target machine:

**Remote (SSH, self-hosted or rented):**
```bash
ssh <server> nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
# rented instances carry their own port/host; for example:
ssh -p <PORT> root@<HOST> nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
```

**Local:**
```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
# or for Mac MPS:
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

Free GPU = `memory.used < 500 MiB`. Never blindly assign a GPU: check first, and if the target GPU is occupied, report which GPU is free instead of stacking jobs on a busy one.

### Step 3: Sync Code (Remote Only)

Check the project's `CLAUDE.md` for a `code_sync` setting. If not specified, default to `rsync`.

#### Option A: rsync (default)

Only sync necessary files — NOT data, checkpoints, or large files:
```bash
rsync -avz --include='*.py' --exclude='*' <local_src>/ <server>:<remote_dst>/
```

#### Option B: git (when `code_sync: git` is set in CLAUDE.md)

Push local changes to the remote repo, then pull on the server:
```bash
# 1. Push from local
git add -A && git commit -m "sync: experiment deployment" && git push

# 2. Pull on server
ssh <server> "cd <remote_dst> && git pull"
```

Benefits: version-tracked, multi-server sync with one push, no rsync include/exclude rules needed.

#### Option C: Rented instance

Sync code to the instance with an explicit include/exclude list (typical remote code dir `/workspace/project/`):
```bash
rsync -avz -e "ssh -p <PORT>" \
  --include='*.py' --include='*.yaml' --include='*.yml' --include='*.json' \
  --include='*.txt' --include='*.sh' --include='*/' \
  --exclude='*.pt' --exclude='*.pth' --exclude='*.ckpt' \
  --exclude='__pycache__' --exclude='.git' --exclude='data/' \
  --exclude='wandb/' --exclude='outputs/' \
  ./ root@<HOST>:/workspace/project/
```

Install dependencies per the env contract (ordered phases — pins first, one
`pip install` per phase; see `references/compute-env-contract.md`):
```bash
ssh -p <PORT> root@<HOST> "pip install -q torch==<pinned>"       # phase 1: pins
ssh -p <PORT> root@<HOST> "pip install -q <remaining packages>"  # phase 2+
```
Legacy fallback — `requirements.txt` only, no env spec: install as one phase, and treat any
version fight as the signal to convert to ordered phases:
```bash
scp -P <PORT> requirements.txt root@<HOST>:/workspace/
ssh -p <PORT> root@<HOST> "pip install -q -r /workspace/requirements.txt"
```

### Step 3.5: W&B Integration (when `wandb: true` in CLAUDE.md)

**Skip this step entirely if `wandb` is not set or is `false` in CLAUDE.md.**

Before deploying, ensure the experiment scripts have W&B logging:

1. **Check if wandb is already in the script** — look for `import wandb` or `wandb.init`. If present, skip to Step 4.

2. **If not present, add W&B logging** to the training script:
   ```python
   import wandb
   wandb.init(project=WANDB_PROJECT, name=EXP_NAME, config={...hyperparams...})

   # Inside training loop:
   wandb.log({"train/loss": loss, "train/lr": lr, "step": step})

   # After eval:
   wandb.log({"eval/loss": eval_loss, "eval/ppl": ppl, "eval/accuracy": acc})

   # At end:
   wandb.finish()
   ```

3. **Metrics to log** (add whichever apply to the experiment):
   - `train/loss` — training loss per step
   - `train/lr` — learning rate
   - `eval/loss`, `eval/ppl`, `eval/accuracy` — eval metrics per epoch
   - `gpu/memory_used` — GPU memory (via `torch.cuda.max_memory_allocated()`)
   - `speed/samples_per_sec` — throughput
   - the seed of this run
   - any custom metrics the experiment already computes

4. **Verify wandb login on the target machine:**
   ```bash
   ssh <server> "wandb status"  # should show logged in
   ```
   If not logged in, have the user log in on that machine (`wandb login`, interactive) or
   export `WANDB_API_KEY` in the remote environment. Never paste an API key into a command
   line that lands in logs, shells history, or this conversation — the key is a secret.

> The W&B project name and API key come from the environment / `CLAUDE.md` (see example below). The experiment name is auto-generated from the script name + timestamp.

### Step 4: Deploy

#### Remote (via SSH + screen)

For each experiment, create a dedicated screen session with GPU binding:
```bash
ssh <server> "screen -dmS <exp_name> bash -c '\
  eval \"\$(<conda_path>/conda shell.bash hook)\" && \
  conda activate <env> && \
  CUDA_VISIBLE_DEVICES=<gpu_id> python <script> <args> 2>&1 | tee <log_file>'"
```

#### Rented instance

No conda needed if the provider image already carries the environment. Use the instance's code dir as working dir:
```bash
ssh -p <PORT> root@<HOST> "screen -dmS <exp_name> bash -c '\
  cd /workspace/project && \
  CUDA_VISIBLE_DEVICES=<gpu_id> python <script> <args> 2>&1 | tee /workspace/<log_file>'"
```

After launching, update the `experiment` field in the instance ledger so the run and the billing meter are traceable.

#### Local

```bash
# Linux with CUDA
CUDA_VISIBLE_DEVICES=<gpu_id> python <script> <args> 2>&1 | tee <log_file>

# Mac with MPS (PyTorch uses MPS automatically)
python <script> <args> 2>&1 | tee <log_file>
```

For local long-running jobs, use `run_in_background: true` to keep the conversation responsive.

### Step 5: Verify Launch

**Remote (SSH, incl. rented):**
```bash
ssh <server> "screen -ls"
```

**Local:**
Check the process is running and the GPU is actually allocated.

Do not report a run as launched from the command's exit code alone — confirm the session exists and the log file is growing.

### Step 6: Optional Notification

After deployment is verified, if the project configures its own notifier (a webhook or
notification script the user set up), send the launch summary: which experiments launched,
which GPUs, estimated time. If no notifier is configured, skip silently — no notification
integration is bundled with this resource, and nothing may be sent to a third-party service
without the user's configuration.

### Step 7: Teardown and Cost Accounting (rented compute only)

**Skip this step unless the run used a rented instance that the user approved.**

After the experiment completes (detected by the screen session ending, the log's completion
marker, or an explicit monitor the user asked for):

1. **Download results** from the instance:
   ```bash
   rsync -avz -e "ssh -p <PORT>" root@<HOST>:/workspace/project/results/ ./results/
   ```

2. **Download logs**:
   ```bash
   scp -P <PORT> root@<HOST>:/workspace/*.log ./logs/
   ```

3. **Verify the transfer before destroying anything** — if the local copy is incomplete, stop and report instead of destroying the instance; losing raw results to save a few minutes of billing is not a trade this resource makes.

4. **Destroy the instance** to stop billing (only if the user opted into auto-teardown for this instance):
   ```bash
   <provider> destroy instance <INSTANCE_ID>
   ```

5. **Update the instance ledger** — mark status as `destroyed`.

6. **Report cost**:
   ```
   Rented instance <ID> destroyed.
   - Duration: ~X.X hours
   - Estimated cost: ~$X.XX
   - Budget cap: $<max_budget> (within / exceeded)
   - Results saved to: ./results/
   ```

> This ensures the user is never billed for idle instances. Never leave a paid instance
> running by default: if it is still alive at the end of the session, say so explicitly and
> ask whether to tear it down.

## Stop Conditions

- **2x the estimated runtime without completion -> flag it and move on.** Report what is
  running, what the log shows, and the cost so far; do not silently extend a run.
- **Projected spend above `max_budget` (when set) -> stop and ask** before launching anything further.
- **A run that cannot be reproduced from its recorded config/seed -> treat as a failed run**, not a result.
- **A sanity check that fails** (data pipeline, metric correctness) -> stop the milestone; do not launch the main stage on top of it.

## Key Rules

- ALWAYS check GPU availability first — never blindly assign GPUs
- Each experiment gets its own screen session + GPU (remote) or background process (local)
- Use `tee` to save logs for later inspection; logs are raw evidence and must not be overwritten
- Run deployment commands with `run_in_background: true` to keep the conversation responsive
- Report back: which GPU, which screen/process, what command, estimated time
- If multiple experiments, launch them in parallel on different GPUs
- Record per run: config, seed(s), library versions, environment — the reproducibility record travels with the results
- **Cost awareness**: report the running cost of rented compute; with an approved budget cap, tear the instance down as soon as all its experiments complete
- **Never auto-spend and never fake a backend**: no hidden provider usage, no simulated deployment reported as real

## Environment Config Example

Users add their compute info to their project's `CLAUDE.md`:

```markdown
## Remote Server
- gpu: remote               # use pre-configured SSH server
- SSH: `ssh my-gpu-server`
- GPU: 4x A100 (80GB each)
- Conda: `eval "$(/opt/conda/bin/conda shell.bash hook)" && conda activate research`
- Code dir: `/home/user/experiments/`
- code_sync: rsync          # default. Or set to "git" for git push/pull workflow
- wandb: false              # set to "true" to auto-add W&B logging to experiment scripts
- wandb_project: my-project # W&B project name (required if wandb: true)
- wandb_entity: my-team     # W&B team/user (optional, uses default if omitted)

## Local Environment
- gpu: local                 # use local GPU
- Mac MPS / Linux CUDA
- Conda env: `ml` (Python 3.10 + PyTorch)
```

For rented compute, the entry looks like:

```markdown
## Rented Instance
- gpu: rented
- provider: <provider name>       # user's own account and CLI, already configured
- max_budget: 5.00                # USD cap for this experiment; exceeding it stops the run
- instances_file: instances.json  # host, port, hourly cost, status, experiment
- auto_teardown: false            # destroy only with the user's explicit approval
```

> Rented compute setup is the user's own: their account, their provider CLI or SSH key,
> their spending limit. This resource never provisions by itself and never handles
> payment credentials.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/run-experiment/SKILL.md (MIT). See registry/components.json. -->
