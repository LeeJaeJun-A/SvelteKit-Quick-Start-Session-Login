<script lang="ts">
  import { goto } from "$app/navigation";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import "izitoast/dist/css/iziToast.min.css";
  import { onDestroy, onMount } from "svelte";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";

  export let toggleForm: () => void;

  let showPassword = false;

  let user_id: string = "";
  let password: string = "";

  async function signInClicked(event: Event) {
    event.preventDefault();

    const iziToast = await import("izitoast").then((module) => module.default);

    if (!user_id || !password) {
      iziToast.error({
        title: "Error",
        message: "All fields are required.",
      });
      return;
    }

    const params = {
      user_id: user_id,
      password: password,
    };

    try {
      await new Promise((resolve, reject) => {
        fastapi("POST", "/login", params, resolve, reject);
      });

      const response = await new Promise<{
        role: string;
      }>((resolve, reject) => {
        fastapi("GET", "/session/role", {}, resolve, reject);
      });

      if (response.role === "admin") {
        goto("/setting");
      } else if (response.role === "user") {
        goto(`/one`);
      }
    } catch (error: any) {
      if (error.detail) {
        iziToast.error({
          title: "Login Failed",
          message: error.detail,
        });
      } else {
        iziToast.error({
          title: "Error",
          message: "An unknown error occurred. Please try again.",
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

<div
  class="w-5/12 h-full border rounded-l-3xl bg-gray-50 flex flex-col p-14"
  style="min-width: 300px;"
>
  <form class="flex-1 flex flex-col justify-center">
    <p class="text-3xl font-bold mb-4 text-gray-800">환영합니다!</p>
    <div class="mb-3 mb-6">
      <label for="id" class="block text-sm font-medium text-gray-700 mb-2"
        >ID</label
      >
      <input
        type="text"
        id="id"
        class="w-full p-3 rounded-lg text-base"
        bind:value={user_id}
        required
        placeholder="아이디를 입력하세요"
      />
    </div>
    <div class="mb-6 relative">
      <label for="password" class="block text-sm font-medium text-gray-700 mb-2"
        >Password</label
      >
      <input
        type={showPassword ? "text" : "password"}
        id="password"
        class="w-full p-3 border rounded-lg text-base"
        required
        bind:value={password}
        placeholder="비밀번호를 입력하세요"
      />
      <button
        type="button"
        tabindex="-1"
        class="absolute inset-y-3 right-0 pr-3 flex items-center text-sm leading-5 h-full select-none"
        on:click={togglePasswordVisibility}
      >
        {#if showPassword}
          <EyeOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
        {:else}
          <EyeSlashOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
        {/if}
      </button>
    </div>
    <button
      type="button"
      class="w-full bg-indigo-700 text-white text-base py-3 mt-6 rounded-lg hover:bg-indigo-800 focus:outline-none"
      on:click={signInClicked}
    >
      로그인
    </button>
    <div class="mt-6 text-sm text-center text-gray-500">
      계정이 없으신가요?
      <button on:click={toggleForm} class="text-indigo-600 hover:underline">
        회원가입
      </button>
    </div>
  </form>
</div>
