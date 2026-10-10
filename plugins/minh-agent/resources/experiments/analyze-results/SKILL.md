# Analyze Experiment Results

When this resource is used: when the user says "analyze results", "compare runs", "what do these numbers say", or experiment outputs exist and need a comparison table, statistics, and interpretation. Analyze: $ARGUMENTS

## Workflow

### Step 1: Locate Results
Find all relevant JSON/CSV result files:
- Check `results/`, `figures/`, `refine-logs/`, or project-specific output directories; parse JSON results into structured data
- Record each file's path — every number in the analysis must trace back to a result file, never to memory or an earlier summary

### Step 2: Build Comparison Table
Organize results by:
- **Independent variables**: model type, hyperparameters, data config, seed
- **Dependent variables**: primary metric, secondary metrics
- **Delta vs baseline**: always compute relative improvement, and state which baseline and which split the delta is against

### Step 3: Statistical Analysis
- If multiple seeds: report mean +/- std across seeds, and check reproducibility (a result that swings across seeds is not a headline result)
- Use Welch's t-test rather than Student's when variance differs; report effect sizes and confidence intervals alongside any significance test, and use Wilson intervals for proportions
- Refuse to test n < 30 without a normality justification — say so instead of reporting a p-value
- If sweeping a parameter: identify trends (monotonic, U-shaped, plateau)
- Flag outliers or suspicious results, including anything that looks too good (metric computed on the wrong split, leaked labels, baseline evaluated under a different protocol)
- Do not pick a favorable seed, subset, or metric after seeing the numbers; if a comparison was not pre-specified, label it exploratory

### Step 4: Generate Insights
For each finding, structure as:
1. **Observation**: what the data shows (with numbers and source file)
2. **Interpretation**: why this might be happening
3. **Implication**: what this means for the research question
4. **Next step**: what experiment would test the interpretation

Keep observation, interpretation, and hypothesis visibly separate — the analysis is not the evidence. Contradictory results are reported with their conditions, never averaged away. Negative results stay in the table.

### Step 5: Update Documentation
If findings are significant:
- Propose updates to project notes or experiment reports, and draft a concise finding statement (1-2 sentences)

## Output Format
Always include:
1. Raw data table (with split, seeds, and source file per row)
2. Key findings (numbered, concise)
3. Suggested next experiments (if any)

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/analyze-results/SKILL.md (MIT). See registry/components.json. -->
