from huggingface_hub import HfApi, hf_hub_download
api = HfApi(); repo = "ouou123/Holo360D"
files = api.list_repo_files(repo, repo_type="dataset")   # names only, nothing downloaded
test = [f for f in files if f.startswith("test/")]
print(len(test)); print(test[:40])                        # inspect the real layout first