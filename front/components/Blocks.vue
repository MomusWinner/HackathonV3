<script lang="ts" setup>
import { marked } from "marked";
const { blocks } = defineProps<{ blocks: Block[] }>();
</script>
<template>
	<div class="flex flex-col gap-2">
		<div
			v-for="(block, i) of blocks"
			:id="i"
			class="bg-primary/5 p-2 rounded-xl"
		>
			<div class="text-md font-medium">{{ block.title }}</div>
			<div
				v-html="marked(block.summary)"
				class="prose prose-stone max-w-none"
			></div>
		</div>
	</div>
</template>
