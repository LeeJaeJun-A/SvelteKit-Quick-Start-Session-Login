<script lang="ts">
  import {
    setMode,
    options,
    mode,
  } from "$lib/components/management/management.ts";
  import { logout } from "$lib/components/login/login.ts";
</script>

<nav
  class="fixed flex flex-col justify-between items-start w-72 h-screen border-r border-[#EBEDEF] bg-white z-40"
>
  <header class="flex items-center justify-between w-full h-14 p-4 pl-6 gap-3">
    <p class="text-xl">관리자 페이지</p>
  </header>
  <div
    class="flex flex-col items-start justify-start space-y-2 w-full flex-grow"
  >
    <ul class="flex flex-col items-center w-full gap-2">
      <button
        class={`flex items-center w-[248px] h-[42px] rounded-lg px-3 py-2 gap-2 hover:bg-blue-50 hover:text-blue-500 ${$mode === options[0] ? "bg-blue-50 text-blue-500" : " bg-white text-[#9AA3B1]"}`}
        onclick={() => {
          setMode(options[0]);
        }}
        tabindex="0"
      >
        <svg
          class={`flex-shrink-0 w-5 h-5 transition duration-75 flex ${
            $mode === options[0] ? "text-blue-500" : "text-[#9AA3B1]"
          }`}
          width="20"
          height="20"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="currentColor"
          viewBox="0 -2 20 20"
        >
          <path
            d="M14 2a3.963 3.963 0 0 0-1.4.267 6.439 6.439 0 0 1-1.331 6.638A4 4 0 1 0 14 2Zm1 9h-1.264A6.957 6.957 0 0 1 15 15v2a2.97 2.97 0 0 1-.184 1H19a1 1 0 0 0 1-1v-1a5.006 5.006 0 0 0-5-5ZM6.5 9a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9ZM8 10H5a5.006 5.006 0 0 0-5 5v2a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-2a5.006 5.006 0 0 0-5-5Z"
          />
        </svg>
        <p
          class={`pl-1 pr-1 ${
            $mode === options[0] ? "text-blue-500" : "text-[#9AA3B1]"
          }`}
        >
          계정 관리
        </p>
      </button>
    </ul>
    <ul class="flex flex-col items-center w-full gap-2">
      <button
        class={`flex items-center w-[248px] h-[42px] rounded-lg px-3 py-2 gap-2 hover:bg-blue-50 hover:text-blue-500 ${$mode === options[1] ? "bg-blue-50 text-blue-500" : " bg-white text-[#9AA3B1]"}`}
        onclick={() => {
          setMode(options[1]);
        }}
        tabindex="0"
      >
        <svg
          class={`flex-shrink-0 w-5 h-5 transition duration-75 flex ${
            $mode === options[1] ? "text-blue-500" : "text-[#9AA3B1]"
          }`}
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            d="M12 7.205c4.418 0 8-1.165 8-2.602C20 3.165 16.418 2 12 2S4 3.165 4 4.603c0 1.437 3.582 2.602 8 2.602ZM12 22c4.963 0 8-1.686 8-2.603v-4.404c-.052.032-.112.06-.165.09a7.75 7.75 0 0 1-.745.387c-.193.088-.394.173-.6.253-.063.024-.124.05-.189.073a18.934 18.934 0 0 1-6.3.998c-2.135.027-4.26-.31-6.3-.998-.065-.024-.126-.05-.189-.073a10.143 10.143 0 0 1-.852-.373 7.75 7.75 0 0 1-.493-.267c-.053-.03-.113-.058-.165-.09v4.404C4 20.315 7.037 22 12 22Zm7.09-13.928a9.91 9.91 0 0 1-.6.253c-.063.025-.124.05-.189.074a18.935 18.935 0 0 1-6.3.998c-2.135.027-4.26-.31-6.3-.998-.065-.024-.126-.05-.189-.074a10.163 10.163 0 0 1-.852-.372 7.816 7.816 0 0 1-.493-.268c-.055-.03-.115-.058-.167-.09V12c0 .917 3.037 2.603 8 2.603s8-1.686 8-2.603V7.596c-.052.031-.112.059-.165.09a7.816 7.816 0 0 1-.745.386Z"
          />
        </svg>

        <p
          class={`pl-1 pr-1 ${
            $mode === options[1] ? "text-blue-500" : "text-[#9AA3B1]"
          }`}
        >
          로그 데이터
        </p>
      </button>
    </ul>
    <ul class="flex flex-col items-center w-full gap-2">
      <button
        class={`flex items-center w-[248px] h-[42px] rounded-lg px-3 py-2 gap-2 hover:bg-blue-50 hover:text-blue-500 bg-white text-[#9AA3B1]`}
        onclick={() => {
          logout();
        }}
        tabindex="0"
      >
        <svg
          class={`flex-shrink-0 w-5 h-5 transition duration-75 flex`}
          width="20"
          height="20"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="-3 0 24 20"
        >
          <path
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M20 12H8m12 0-4 4m4-4-4-4M9 4H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h2"
          />
        </svg>
        <p class={`pl-1 pr-1`}>로그아웃</p>
      </button>
    </ul>

  </div>
</nav>
