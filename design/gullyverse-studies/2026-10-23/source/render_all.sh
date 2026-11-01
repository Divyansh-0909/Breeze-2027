#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd "$(dirname "$0")/.." && pwd)"
blender -b -t 2 --python "$task_root/source/build_scene.py"
blender -b "$task_root/source/Gullyverse-Lane-Rooftop-ABC.blend" -t 2 --python "$task_root/source/calibrate_scene.py"
blender -b "$task_root/source/Gullyverse-Lane-Rooftop-ABC.blend" -t 1 --python "$task_root/source/validate_concept.py"
blender -b "$task_root/source/Gullyverse-Lane-Rooftop-ABC.blend" -t 1 --python "$task_root/source/audit_scene.py"
blender -b "$task_root/source/Gullyverse-Lane-Rooftop-ABC.blend" -t 2 --python "$task_root/source/render_study.py" -- final
blender -b "$task_root/source/Gullyverse-Lane-Rooftop-ABC.blend" -t 2 --python "$task_root/source/render_study.py" -- animatic
python "$task_root/source/draw_layout.py"
python "$task_root/source/write_report.py"
python "$task_root/source/make_review.py"
