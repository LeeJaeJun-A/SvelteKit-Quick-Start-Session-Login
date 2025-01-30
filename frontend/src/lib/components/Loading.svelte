<div class="flex flex-col justify-center items-center h-screen">
  <div class="relative flex flex-col justify-center items-center w-full h-full">
    <div class="relative flex justify-center items-center w-full h-full">
      {#each Array(6).fill(0) as _, i}
        <div
          class="absolute w-15 h-15 animate-rotate 4xl:w-32 4xl:h-32"
          style="animation-delay: {0.15 * i}s;"
        >
          <div
            class="relative top-7 w-2.5 h-2.5 rounded-full bg-blue-500 4xl:w-4 4xl:h-4"
          ></div>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  @keyframes rotate {
    30% {
      transform: rotate(220deg);
    }
    40% {
      transform: rotate(450deg);
    }
    75% {
      transform: rotate(720deg);
      opacity: 1;
    }
    76% {
      opacity: 0;
    }
    100% {
      transform: rotate(0deg);
      opacity: 0;
    }
  }

  .animate-rotate {
    animation: rotate 2s linear infinite;
  }
</style>
