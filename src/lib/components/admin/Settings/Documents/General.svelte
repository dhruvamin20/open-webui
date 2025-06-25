<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import ArrowDownTray from '$lib/components/icons/ArrowDownTray.svelte';
	import { config } from '$lib/stores';
	// import { exportAllKnowledge } from '$lib/apis/knowledge';

	const i18n = getContext('i18n');

	export let updateHandler = () => {};
	export let RAGConfig = null;
</script>

<div class="mb-2 text-sm font-medium">{$i18n.t('General Settings')}</div>

<div class="flex flex-col space-y-3">
	{#if $config?.features?.enable_admin_export ?? true}
		<div>
			<div class="py-0.5 flex w-full justify-between">
				<div class="self-center text-xs font-medium">
					{$i18n.t('Export Documents Workspace')}
				</div>

				<button
					class="text-xs px-3 py-1.5 rounded flex gap-1 items-center bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition"
					type="button"
					on:click={async () => {
						// TODO: Implement exportAllKnowledge function
						toast.info($i18n.t('Export functionality not yet implemented'));
						/*
						const res = await exportAllKnowledge(localStorage.token).catch((error) => {
							toast.error(`${error}`);
							return null;
						});

						if (res) {
							const blob = new Blob([res], { type: 'application/gzip' });
							const url = URL.createObjectURL(blob);
							const a = document.createElement('a');
							a.href = url;
							a.download = 'knowledge-export.tar.gz';
							document.body.appendChild(a);
							a.click();
							document.body.removeChild(a);
							URL.revokeObjectURL(url);
							toast.success($i18n.t('Knowledge exported successfully'));
						}
						*/
					}}
				>
					<ArrowDownTray className="size-3" />
					{$i18n.t('Export All')}
				</button>
			</div>
		</div>
	{/if}

	{#if RAGConfig}
		<hr class="dark:border-gray-850 my-2" />

		<div class="space-y-3">
			<div class="flex flex-col gap-2">
				<div class="text-sm font-medium">{$i18n.t('Advanced Retrieval Settings')}</div>
				
				<div>
					<label class="flex items-center text-xs">
						<input
							type="checkbox"
							class="mr-2"
							bind:checked={RAGConfig.USE_ADVANCED_RETRIEVAL}
							on:change={() => {
								updateHandler();
							}}
						/>
						{$i18n.t('Enable Advanced Retrieval')}
					</label>
				</div>

				{#if RAGConfig.USE_ADVANCED_RETRIEVAL}
					<div class="ml-4 space-y-2">
						<div>
							<label class="flex items-center text-xs">
								<input
									type="checkbox"
									class="mr-2"
									bind:checked={RAGConfig.ENABLE_QUERY_EXPANSION}
									on:change={() => {
										updateHandler();
									}}
								/>
								{$i18n.t('Enable Query Expansion')}
							</label>
						</div>

						<div>
							<label class="flex items-center text-xs">
								<input
									type="checkbox"
									class="mr-2"
									bind:checked={RAGConfig.ENABLE_DOCUMENT_RERANKING}
									on:change={() => {
										updateHandler();
									}}
								/>
								{$i18n.t('Enable Document Reranking')}
							</label>
						</div>

						<div>
							<label class="flex items-center text-xs">
								<input
									type="checkbox"
									class="mr-2"
									bind:checked={RAGConfig.ENABLE_SEMANTIC_CHUNKING}
									on:change={() => {
										updateHandler();
									}}
								/>
								{$i18n.t('Enable Semantic Chunking')}
							</label>
						</div>

						<div class="flex flex-col gap-1">
							<label class="text-xs font-medium">{$i18n.t('Chat Upload Processing Mode')}</label>
							<select
								class="w-full rounded-lg py-2 px-3 text-xs bg-gray-50 dark:bg-gray-850 dark:text-gray-100"
								bind:value={RAGConfig.CHAT_UPLOAD_PROCESSING_MODE}
								on:change={() => {
									updateHandler();
								}}
							>
								<option value="full_context">{$i18n.t('Full Context')}</option>
								<option value="chunked_vectorized">{$i18n.t('Chunked & Vectorized')}</option>
								<option value="hybrid">{$i18n.t('Hybrid')}</option>
							</select>
						</div>

						<div class="flex flex-col gap-1">
							<label class="text-xs font-medium">{$i18n.t('Knowledge Base Processing Mode')}</label>
							<select
								class="w-full rounded-lg py-2 px-3 text-xs bg-gray-50 dark:bg-gray-850 dark:text-gray-100"
								bind:value={RAGConfig.KNOWLEDGE_BASE_PROCESSING_MODE}
								on:change={() => {
									updateHandler();
								}}
							>
								<option value="full_context">{$i18n.t('Full Context')}</option>
								<option value="chunked_vectorized">{$i18n.t('Chunked & Vectorized')}</option>
								<option value="hybrid">{$i18n.t('Hybrid')}</option>
							</select>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<hr class="dark:border-gray-850 my-2" />

		<div>
			<div class="mb-2 text-sm font-medium">{$i18n.t('File Upload Limit')}</div>
			
			<div class="flex w-full gap-2">
				<div class="flex-1">
					<label class="text-xs font-medium mb-1">{$i18n.t('Max File Size (MB)')}</label>
					<input
						type="number"
						class="w-full rounded-lg py-2 px-3 text-xs bg-gray-50 dark:bg-gray-850 dark:text-gray-100"
						placeholder={$i18n.t('No limit')}
						bind:value={RAGConfig.FILE_MAX_SIZE}
						on:change={() => {
							updateHandler();
						}}
					/>
				</div>
				
				<div class="flex-1">
					<label class="text-xs font-medium mb-1">{$i18n.t('Max File Count')}</label>
					<input
						type="number"
						class="w-full rounded-lg py-2 px-3 text-xs bg-gray-50 dark:bg-gray-850 dark:text-gray-100"
						placeholder={$i18n.t('No limit')}
						bind:value={RAGConfig.FILE_MAX_COUNT}
						on:change={() => {
							updateHandler();
						}}
					/>
				</div>
			</div>
		</div>
	{/if}
</div> 