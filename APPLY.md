# Apply clean README patch

Copy this patch into the repository root and run:

```bash
cp -a ~/Downloads/readme_clean_no_presentation_patch/. ~/Downloads/modulehandbook-rag/
cd ~/Downloads/modulehandbook-rag
bash scripts/cleanup_submission_files.sh
git add -A
git commit -m "Clean public README"
git push origin main
```
