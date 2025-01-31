<script lang="ts">
  import { setMode } from "$lib/components/management/management.ts";
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import MenuBar from "$lib/components/management/MenuBar.svelte";
  import Log from "$lib/components/management/log/Log.svelte";
  import UserManagement from "$lib/components/management/user/UserManagement.svelte";
  import { options, mode } from "$lib/components/management/management.ts";
  import Loading from "$lib/components/Loading.svelte";
  import { goto } from "$app/navigation";
  import fastapi from "$lib/components/utils/fastapi.ts";

  let loading = true;

  onMount(async () => {
    try {
      if (browser) {
        const response = await new Promise<{
          role: string;
        }>((resolve, reject) => {
          fastapi("GET", "/session/role", {}, resolve, reject);
        });

        if (response.role === "user") {
          goto("/one", { replaceState: true });
        } else {
          setMode(options[0]);
          loading = false;
        }
      }
    } catch {
      goto("/login", { replaceState: true });
    }
  });
</script>

{#if loading}
  <Loading />
{:else}
  <div class="flex h-screen">
    <div class="w-72 bg-red-500 shrink-0">
      <MenuBar />
    </div>
    <div class="flex-1 overflow-x-hidden">
      {#if $mode === options[0]}
        <UserManagement />
      {:else if $mode === options[1]}
        <Log />
      {/if}
    </div>
  </div>
{/if}
