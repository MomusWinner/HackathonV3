<script setup></script>

<template>
<div class="p-5">
    <div class="items-top flex gap-x-2">
        <Checkbox id="terms1" />
        <div class="grid gap-1.5 leading-none">
            <label
              for="terms1"
              class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
            Теги
            </label>
            <p class="text-sm text-muted-foreground">
            Oписание
            </p>
        </div>
    </div>
    <div class="items-top flex gap-x-2">
        <Checkbox id="terms1" />
        <div class="grid gap-1.5 leading-none">
            <label
              for="terms1"
              class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
            Анализ изображения
            </label>
            <p class="text-sm text-muted-foreground">
            Oписание
            </p>
        </div>
    </div>
    <div class="items-top flex gap-x-2">
        <Checkbox id="terms1" />
        <div class="grid gap-1.5 leading-none">
            <label
              for="terms1"
              class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
            Рекомендации
            </label>
            <p class="text-sm text-muted-foreground">
            Oписание
            </p>
        </div>
    </div>
    <br>
    <Textarea class="w-full" placeholder="Type your message here." />
</div>
</template>
