<script lang="ts">
  import SignIn from "$lib/components/login/login_public/SignIn.svelte";
  import SignUp from "$lib/components/login/login_public/SignUp.svelte";
  import type { Writable } from "svelte/store";
  import { get, writable } from "svelte/store";

  let showLogin: Writable<Boolean> = writable(true);

  function toggleForm() {
    showLogin.set(!get(showLogin));
  }
</script>

<main class="flex h-screen w-screen justify-center items-center">
  <div
    class="flex shadow-lg rounded-3xl overflow-hidden"
    style="width: 60%; height:70%"
  >
    {#if $showLogin}
      <SignIn {toggleForm} />
    {:else}
      <SignUp {toggleForm} />
    {/if}
    <div
      class="w-7/12 h-full border rounded-r-3xl flex justify-center items-center bg-white relative"
    >
      <!-- <img src="/logo.png" class="select-none" alt="logo" /> -->
    </div>
  </div>
</main>
