<script lang="ts" setup>
import { Badge } from "@/components/ui/badge";
const { tags } = defineProps<{ tags: string[] }>();
</script>

<template>
	<div class="flex gap-2">
		<div v-for="(tag, i) of tags" :id="i">
			<Badge variant="outline" class="rounded-xl">{{ tag }}</Badge>
		</div>
	</div>
</template>
