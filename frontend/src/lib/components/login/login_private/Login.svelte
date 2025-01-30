<script lang="ts">
  import { goto } from "$app/navigation";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import "izitoast/dist/css/iziToast.min.css";
  import { onDestroy, onMount } from "svelte";
  import { Button, Label, Input } from "flowbite-svelte";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";
  import { hashPassword } from "$lib/components/utils/hash.ts";

  let showPassword = false;

  let id: string = "";
  let password: string = "";

  async function signInClicked(event: Event) {
    event.preventDefault();

    const iziToast: any = await import("izitoast").then(
      (module) => module.default
    );

    if (!id || !password) {
      iziToast.error({
        title: "오류",
        message: "모든 필드를 입력해 주세요.",
      });
      return;
    }

    const hashedPassword = hashPassword(password);
    const params = { user_id: id, password: hashedPassword };

    try {
      await new Promise((resolve, reject) => {
        fastapi("POST", "/login", params, resolve, reject);
      });

      const response = await new Promise<{
        role: string;
      }>((resolve, reject) => {
        fastapi("GET", "/session/role", {} , resolve, reject);
      });

      if (response.role === "admin") {
        await goto("/setting");
      } else if (response.role === "user") {
        await goto(`/`);
      }
    } catch (error: any) {
      if (error.detail) {
        iziToast.error({
          title: "로그인 실패",
          message: error.detail,
        });
      } else {
        iziToast.error({
          title: "오류",
          message: "알 수 없는 오류가 발생했습니다. 다시 시도해 주세요.",
        });
      }
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      event.preventDefault();
      signInClicked(new Event("submit") as SubmitEvent);
    }
  }

  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }

  onMount(() => {
    if (typeof window !== "undefined") {
      document.addEventListener("keydown", handleKeyDown);
    }
  });

  onDestroy(() => {
    if (typeof window !== "undefined") {
      document.removeEventListener("keydown", handleKeyDown);
    }
  });
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
  <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
    <h2 class="text-2xl font-bold mb-6 text-center">로그인</h2>
    <form class="space-y-6">
      <div>
        <Label for="id">아이디</Label>
        <Input id="id" bind:value={id} autocomplete="username" required />
      </div>
      <div class="relative">
        <Label for="password">비밀번호</Label>
        <Input
          id="password"
          type={showPassword ? "text" : "password"}
          bind:value={password}
          autocomplete="current-password"
          required
        />
        <button
          type="button"
          class="absolute inset-y-0 right-0 py-10 pr-3 flex items-center text-sm leading-5 h-full"
          on:click={togglePasswordVisibility}
        >
          {#if showPassword}
            <EyeOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {:else}
            <EyeSlashOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {/if}
        </button>
      </div>
      <Button
        type="button"
        class="bg-indigo-700  hover:bg-indigo-800 w-full justify-center flex focus:outline-none focus:ring-0"
        on:click={signInClicked}
      >
        로그인
      </Button>
    </form>
  </div>
</div>
