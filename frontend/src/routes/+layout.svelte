<script lang="ts">
  import Header from "$lib/components/header.svelte";
  import "../app.css";
</script>

<svelte:head>
  <title>Title</title>
</svelte:head>

<main>
  <Header />
  <slot />
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    min-height: 100%;
  }
</style>
