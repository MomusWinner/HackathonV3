<script lang="ts" setup>
const { header } = defineProps<{
	header: string;
}>();
</script>

<template>
	<div class="flex flex-col gap-2">
		<div class="text-2xl font-medium">{{ header }}</div>
		<div class="bg-primary/5 p-2 rounded-lg">
			<slot />
		</div>
	</div>
</template>
