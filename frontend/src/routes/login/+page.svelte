<script lang="ts">
  import Login from "$lib/components/login/Login.svelte";
  import Loading from "$lib/components/Loading.svelte";
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import { goto } from "$app/navigation";
  import fastapi from "$lib/components/utils/fastapi.ts";

  let loading = true;

  onMount(async () => {
    if (browser) {
      const response = await new Promise<{
        role: string;
      }>((resolve, reject) => {
        fastapi("GET", "/session/role", {}, resolve, reject);
      });
      if (response.role === "admin") {
        goto("/setting", { replaceState: true });
      } else if (response.role === "user") {
        goto("/one", { replaceState: true });
      } else {
        loading = false;
      }
    }
  });
</script>

{#if loading}
  <Loading />
{:else}
  <Login />
{/if}
