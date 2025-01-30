<script lang="ts">
  import Swal from "sweetalert2";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import { hashPassword } from "$lib/components/utils/hash.ts";

  export let onClose;
  export let user_id: string;

  let old_password: string = "";
  let new_password: string = "";

  const handleSubmit = async (event: Event) => {
    event.preventDefault();

    try {
      await new Promise((resolve, reject) => {
        fastapi(
          "POST",
          "/user/change/password/",
          {
            user_id: user_id,
            old_password: hashPassword(old_password),
            new_password: hashPassword(new_password),
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
      <div>
        <label
          for="old_password"
          class="block text-xs font-medium text-gray-700">현재 비밀번호</label
        >
        <input
          id="old_password"
          type="password"
          bind:value={old_password}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
          required
        />
      </div>
      <div>
        <label
          for="new_password"
          class="block text-xs font-medium text-gray-700">새 비밀번호</label
        >
        <input
          id="new_password"
          type="password"
          bind:value={new_password}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
          required
        />
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
