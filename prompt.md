You are operating inside a repository that lets you run an unknown environment locally.

Your goal:
1) Understand the environment dynamics and the win condition for the game ID "ls20" do not change it.
2) Iteratively improve agents/my_agent.py so that it reliably reaches WIN (or maximizes levels_completed) within the action limit.
3) Keep a transparent research trail.

What you can do:
- Run: python run_agent.py  (with optionnal parameters the more important for you is --max-actions)
- Edit code, create helper scripts, and re-run as often as needed.

Process requirements:
- Create a folder checkpoints/ and write short markdown notes after each significant iteration:
  - checkpoints/note_01.md, note_02.md, ...
  Each note must include: what you tested, what you observed from logs/frames, what you changed next.
- If you write any exploration scripts, save them as checkpoints/probe_01.py, probe_02.py, etc and link it with the note associated (by commenting it).
- Keep the final agent implementation in agents/my_agent.py.
- you can comeback check your checkpoints when you are struggling or want to review your research trail, but do not change previous notes.

Final deliverables:
- reports/final_report.md including:
  - inferred objective / win condition
  - key observations about the frame representation (what in the grid matters)
  - final strategy description
  - commands to reproduce
  - results summary (how many runs, win rate, typical steps)
- Ensure the repo runs without extra manual steps.

Do not assume the objective is given in text. You must infer it from interaction (frames, state, available_actions).