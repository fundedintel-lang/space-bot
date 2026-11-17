# space-team

Ek **skill** (AI ka model nahi) jo Claude Code me ek autonomous build loop
chalati hai:

```
Planner → Builder → Checker → (fail?) ↺ Planner
                    ↓ pass
              Master sweep → Judge → Clerk → REPORT.md
```

Loop apne aap ko "ho gaya" nahi keh sakta. Sirf `scripts/verify.py` ka exit 0
loop khatam kar sakta hai, aur fix rounds ki ek limit hai (default 6). Isse
"chalta rehta hai, rukta nahi" wala part control me rehta hai.

## Kaise chalta hai

| Role | Kya karta hai | File |
|---|---|---|
| Planner | Goal + **machine-checkable** Definition of Done + subtasks + physics/maths coverage table | `PLAN.md` |
| Builder | Code + tests likhta hai | `src/`, `tests/` |
| Checker | khud verify karta hai: units/dimensions, conservation laws, limits, numeric residual, independent recompute, web constants | `CHECK_REPORT.md` |
| Planner (fix) | fail hone par fix plan | `PLAN.md` → `## Fix round N` |
| Master | coverage table + boundary/error-budget/assumption sweep | `CHECK_REPORT.md` update |
| Judge | DoD ka audit: planned/built/checked/evidence | `JUDGE.md` |
| Clerk | user ke liye final document | `REPORT.md` |

## Install (2 tareeke)

**A) Claude Code plugin (recommended)**

```
/plugin marketplace add fundedintel-lang/space-bot
/plugin install space-team@space-bot
```

Phir: `/space-team ek double pendulum ka simulation banao jo energy conserve kare`

**B) Manual skill copy**

```bash
git clone https://github.com/fundedintel-lang/space-bot
mkdir -p .claude/skills
cp -r space-bot/skills/space-team .claude/skills/
cp -r space-bot/scripts .claude/skills/space-team/scripts   # ya repo me hi kaam karo
```

Phir Claude Code me: *"space-team skill use karke <goal> banao"*.

## Toolkit (plain Python 3.11+, koi dependency nahi)

```bash
python3 scripts/scaffold.py --name my-project --root projects  # workspace + verify.toml
python3 scripts/verify.py   --project projects/my-project      # gates; exit 0 = done
python3 scripts/plan.py     new|round|status --project ...     # round budget
python3 scripts/topics.py   --domains mechanics,quantum        # coverage checklist
python3 scripts/sanity.py   --demo                             # dimension checker demo
```

`verify.toml` me jo bhi `[[check]]` `required = true` hai, wo pass hona zaroori
hai — warna loop aage nahi badhta.

## Worked example (asli, chalne wala)

`examples/pendulum/` me ek poora loop ka paper trail hai. Usme **jaan-boojh kar**
ek bug tha (numerical path me missing `sqrt(2)`), jo cross-check ne pakda,
fix round 1 me theek hua, aur tolerance kam **nahi** ki gayi:

```bash
python3 scripts/verify.py --project examples/pendulum
# PASS 3/3, 8 unit tests, VERIFY.md generated
```

## Kya ye nahi kar sakta (honest limits)

- Ye naya AI nahi banata; ye wahi Claude hai, 6 roles me. Quality model par
  depend karti hai, skill par nahi.
- "Duniya ke a to z physics topics" enumerate karna infinite hai. `topics.py`
  ek checklist deta hai; asli guarantee Definition of Done + tests dete hain.
- Jo cheez machine-checkable nahi hai (design taste, "achha lagta hai"), uske
  liye loop ka gate kaam nahi karega — wahan Judge ki ranking + user review
  hi final hai.
- Koi bhi physical experiment simulate hi hoga; report me "simulation" likha
  jayega, measurement nahi.
- Cost: har round tokens khata hai. Budget isi liye hai.

## Files

```
.claude-plugin/plugin.json   plugin manifest
commands/space-team.md       /space-team slash command
skills/space-team/SKILL.md   the loop instructions
scripts/                     scaffold, verify, plan, topics, sanity
examples/pendulum/           full worked loop with a real caught bug
```

MIT License.
