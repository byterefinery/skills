# 03 — HfApi surface

The `HfApi` class (in `hf_api.py`) is the full Hub API. Almost everything is also exposed as a module-level convenience function in `huggingface_hub` (verified from the package `__all__`). Grouped by domain:

## Models / Datasets / Spaces

- `list_models(...)`, `list_datasets(...)`, `list_spaces(...)` — search with filters, sorting, pagination
- `search_spaces(...)` — space search
- `model_info(repo_id)`, `dataset_info(repo_id)`, `space_info(repo_id)` — metadata objects (`ModelInfo`, `DatasetInfo`, `SpaceInfo`)
- `list_dataset_parquet_files(...)` — parquet files of a dataset
- `list_space_templates(...)`, `list_spaces_hardware(...)` — space templates and hardware catalog
- `get_model_tags(...)`, `get_dataset_tags(...)` — tag catalogs

## Repos

- `create_repo(repo_id, *, private=None, visibility=None, repo_type=None, exist_ok=False, region=None, space_sdk=None, space_hardware=None, space_sleep_time=None, space_secrets=None, space_variables=None, space_volumes=None, space_template=None, ...)` → `RepoUrl`
- `delete_repo(...)`, `move_repo(...)`, `duplicate_repo(...)`, `update_repo_settings(...)`
- `repo_exists(...)`, `file_exists(...)`, `revision_exists(...)`
- `repo_info(repo_id, repo_type=None, revision=None)` — generic repo metadata
- `list_repo_files(...)`, `list_repo_tree(...)`, `get_paths_info(...)`, `get_hf_file_metadata(...)`
- `list_repo_commits(...)`, `list_repo_refs(...)`, `resolve_revision(...)`
- `verify_repo_checksums(...)`, `super_squash_history(...)`, `get_full_repo_name(...)`
- `get_cached_repo_tree(...)` — tree from the local cache

## Branches and tags

- `create_branch(...)`, `delete_branch(...)`, `create_tag(...)`, `delete_tag(...)`

## Discussions and PRs

- `create_discussion(...)`, `get_repo_discussions(...)`, `get_discussion_details(...)`
- `comment_discussion(...)`, `edit_discussion_comment(...)`, `change_discussion_status(...)`, `rename_discussion(...)`
- `create_pull_request(...)`, `merge_pull_request(...)`

## Collections

- `create_collection(...)`, `list_collections(...)`, `get_collection(...)`
- `add_collection_item(...)`, `update_collection_item(...)`, `delete_collection_item(...)`
- `update_collection_metadata(...)`, `update_collection_resource_group(...)`, `delete_collection(...)`
- `list_liked_repos(...)`, `unlike(...)`

## Papers

- `list_papers(...)`, `list_daily_papers(...)`, `paper_info(...)`

## Webhooks

- `create_webhook(...)`, `list_webhooks(...)`, `get_webhook(...)`, `update_webhook(...)`
- `delete_webhook(...)`, `enable_webhook(...)`, `disable_webhook(...)`
- `webhook_endpoint(...)` — endpoint URL helper
- Payload types: `WebhookPayload`, `WebhookPayloadRepo`, `WebhookPayloadDiscussion`, `WebhookPayloadComment`, `WebhookPayloadEvent`, `WebhookPayloadUrl`, `WebhookPayloadWebhook`, `WebhookPayloadMovedTo`, `WebhookPayloadDiscussionChanges`
- `WebhooksServer` — run a webhook-receiving server locally

## Organizations and users

- `list_organization_members(...)`, `list_organization_followers(...)`, `get_organization_overview(...)`
- `list_user_followers(...)`, `list_user_following(...)`, `list_user_repos(...)`, `get_user_overview(...)`
- `list_repo_likers(...)`, `UserLikes`, `User`, `Organization`

## Inference endpoints (deployment)

- `create_inference_endpoint(...)`, `create_inference_endpoint_from_catalog(...)`
- `list_inference_endpoints(...)`, `get_inference_endpoint(...)`, `update_inference_endpoint(...)`
- `delete_inference_endpoint(...)`, `pause_inference_endpoint(...)`, `resume_inference_endpoint(...)`, `scale_to_zero_inference_endpoint(...)`
- `list_inference_endpoints_hardware(...)`, `list_inference_catalog(...)`
- Types: `InferenceEndpoint`, `InferenceEndpointHardware`, `InferenceEndpointStatus`, `InferenceEndpointType`, `InferenceCatalogModel`, `InferenceCatalogRecipe`

## Spaces runtime

- `get_space_runtime(...)`, `get_space_secrets(...)`, `get_space_variables(...)`
- `add_space_secret(...)`, `add_space_variable(...)`, `delete_space_secret(...)`, `delete_space_variable(...)`
- `set_space_volumes(...)`, `delete_space_volumes(...)`
- `set_space_sleep_time(...)`, `pause_space(...)`, `restart_space(...)`, `wait_for_space(...)`
- `request_space_hardware(...)`, `enable_space_dev_mode(...)`, `disable_space_dev_mode(...)`
- `fetch_space_logs(...)`, `search_spaces(...)`

## Eval results and misc

- `metadata_eval_result(...)`, `parse_eval_result_entries(...)`, `eval_result_entries_to_yaml(...)`
- `EvalResult`, `EvalResultEntry`
- `upload_attachment(...)` — file attachments for comments/discussions
- `CommitScheduler` / `create_scheduled_uv_job(...)` — scheduled background commits and UV jobs
