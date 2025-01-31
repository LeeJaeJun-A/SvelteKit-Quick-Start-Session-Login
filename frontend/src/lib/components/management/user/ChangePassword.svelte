<script lang="ts">
  import Swal from "sweetalert2";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";

  export let onClose;
  export let user_id: string;

  let showCurrentPassword = false;
  let showNewPassword = false;

  let old_password: string = "";
  let new_password: string = "";

  const handleSubmit = async (event: Event) => {
    event.preventDefault();

    try {
      await new Promise((resolve, reject) => {
        fastapi(
          "POST",
          "/user/change/password",
          {
            user_id: user_id,
            old_password: old_password,
            new_password: new_password,
          },
          resolve,
          reject
        );
      });

      Swal.fire("성공", "비밀번호가 성공적으로 변경되었습니다.", "success");
      onClose();
    } catch (error: any) {
      Swal.fire(
        "오류",
        error.detail || "비밀번호를 변경하는 중 오류가 발생했습니다.",
        "error"
      );
    }
  };
</script>

<section
  class="bg-white rounded-lg p-8 flex flex-col justify-evenly items-center w-full h-full select-none"
>
  <span class="text-xl mb-6">비밀번호 변경</span>
  <div class="w-full">
    <form
      on:submit|preventDefault={handleSubmit}
      class="w-full flex flex-col space-y-6"
    >
      <div>
        <p class="block text-xs font-medium text-gray-700">아이디</p>
        <p
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
        >
          {user_id}
        </p>
      </div>
      <div class="relative">
        <label
          for="old_password"
          class="block text-xs font-medium text-gray-700">현재 비밀번호</label
        >
        <input
          id="old_password"
          type={showCurrentPassword ? "text" : "password"}
          bind:value={old_password}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
          required
        />
        <button
          type="button"
          class="absolute inset-y-0 right-0 py-10 pr-3 flex items-center text-sm leading-5 h-full"
          on:click={() => {
            showCurrentPassword = !showCurrentPassword;
          }}
        >
          {#if showCurrentPassword}
            <EyeOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {:else}
            <EyeSlashOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {/if}
        </button>
      </div>
      <div class="relative">
        <label
          for="new_password"
          class="block text-xs font-medium text-gray-700">새 비밀번호</label
        >
        <input
          id="new_password"
          type={showNewPassword ? "text" : "password"}
          bind:value={new_password}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
          required
        />
        <button
          type="button"
          class="absolute inset-y-0 right-0 py-10 pr-3 flex items-center text-sm leading-5 h-full"
          on:click={() => {
            showNewPassword = !showNewPassword;
          }}
        >
          {#if showNewPassword}
            <EyeOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {:else}
            <EyeSlashOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {/if}
        </button>
      </div>
      <div class="flex pt-4 space-x-4 justify-center w-full pt-2">
        <button
          type="submit"
          class="flex w-16 h-8 justify-center items-center bg-blue-600 text-white text-sm rounded-md shadow-sm"
        >
          변경
        </button>
        <button
          type="button"
          on:click={onClose}
          class="flex w-16 h-8 justify-center items-center bg-gray-600 text-white text-sm rounded-md shadow-sm"
        >
          닫기
        </button>
      </div>
    </form>
  </div>
</section>
