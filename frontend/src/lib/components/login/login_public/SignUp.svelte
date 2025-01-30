<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import "izitoast/dist/css/iziToast.min.css";

  export let toggleForm: () => void;

  let user_id: string = "";
  let password: string = "";
  let confirm_password: string = "";

  async function signUpClicked(event: Event) {
    event.preventDefault?.();

    const iziToast = await import("izitoast").then((module) => module.default);

    if (!user_id || !password || !confirm_password) {
      iziToast.error({
        title: "Error",
        message: "All fields are required.",
      });
      return;
    }

    if (password !== confirm_password) {
      iziToast.error({
        title: "Error",
        message: "Passwords do not match.",
      });
      return;
    }

    if (password.length < 8) {
      iziToast.error({
        title: "Error",
        message: "Password must be at least 8 characters long.",
      });
      return;
    }

    const params = {
      user_id: user_id,
      password: password,
      role: "user"
    };

    // need to change backend code
    // because in private mode, api needs session cookies.
    try {
      await new Promise<void>((resolve, reject) => {
        fastapi("POST", "/user/", params, resolve, reject);
      });

      iziToast.success({
        title: "Success",
        message: "Account created successfully!",
      });

      toggleForm();
    } catch (error: any) {
      console.log("Error object:", error);

      if (error.detail && error.detail.includes("Email already registered")) {
        // 409 Conflict
        iziToast.error({
          title: "Error",
          message:
            "This user_id is already registered. Please use a different user_id.",
        });
      } else if (error.message) {
        iziToast.error({
          title: "Error",
          message: error.message,
        });
      } else {
        iziToast.error({
          title: "Error",
          message: "An unknown error occurred.",
        });
      }
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      event.preventDefault();
      signUpClicked(new Event("submit"));
    }
  }

  onMount(() => {
    window.addEventListener("keydown", handleKeyDown);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleKeyDown);
  });
</script>

<div class="w-5/12 h-full border rounded-l-3xl bg-gray-50 flex flex-col p-14">
  <form class="flex-1 flex flex-col justify-center">
    <p class="text-3xl font-bold mb-4 text-gray-800">회원가입</p>
    <div class="mb-3 4xl:mb-6">
      <label
        for="user_id"
        class="block text-xs 4xl:text-sm font-medium text-gray-700 mb-2"
        >ID</label
      >
      <input
        type="text"
        id="user_id"
        class="w-full p-2 4xl:p-3 border rounded-lg text-xs 4xl:text-base"
        bind:value={user_id}
        placeholder="아이디를 입력하세요"
        required
      />
    </div>
    <div class="mb-6">
      <label for="password" class="block text-sm font-medium text-gray-700 mb-2"
        >Password</label
      >
      <input
        type="password"
        id="password"
        class="w-full p-3 border rounded-lg text-base"
        required
        bind:value={password}
        placeholder="비밀번호를 입력하세요"
      />
    </div>
    <div class="mb-6">
      <label
        for="confirm-password"
        class="block text-xs 4xl:text-sm font-medium text-gray-700 mb-2"
        >Confirm Password</label
      >
      <input
        type="password"
        id="confirm-password"
        class="w-full p-2 4xl:p-3 border rounded-lg text-xs 4xl:text-base"
        bind:value={confirm_password}
        placeholder="비밀번호를 한 번 더 입력하세요"
        required
      />
    </div>
    <button
      type="button"
      class="w-full bg-indigo-600 text-white text-xs 4xl:text-base py-2 4xl:py-3 4xl:mt-6 rounded-lg hover:bg-indigo-700 transition duration-300 ease-in-out"
      on:click={signUpClicked}
    >
      계정 등록
    </button>
    <div class="mt-4 4xl:mt-6 text-xs 4xl:text-sm text-center text-gray-500">
      이미 계정이 있으신가요?
      <button
        type="button"
        on:click={toggleForm}
        class="text-indigo-600 hover:underline"
      >
        로그인
      </button>
    </div>
  </form>
</div>
