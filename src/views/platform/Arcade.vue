<template>
  <div class="arcade-page platform-page container layout-single">
    <header class="arcade-hero platform-panel ink-panel">
      <p class="platform-coord">ARCADE · MIND · LAB</p>
      <h1 class="arcade-title">奇怪的游戏厅</h1>
      <p class="arcade-lead">
        一间收集<strong>冷门认知小游戏</strong>的实验室 —— 测测你的注意力、反应力和工作记忆。
        全部本地运行，成绩只存在你自己的浏览器里。
      </p>
    </header>

    <section class="arcade-gallery">
      <router-link
        v-for="game in games"
        :key="game.to"
        :to="game.to"
        class="arcade-game-card platform-panel"
      >
        <span class="arcade-game-glyph" aria-hidden="true">{{ game.glyph }}</span>
        <div class="arcade-game-main">
          <h2 class="arcade-game-name">{{ game.name }}</h2>
          <p class="arcade-game-tag">{{ game.tag }}</p>
          <p class="arcade-game-desc">{{ game.desc }}</p>
        </div>
        <span class="arcade-game-go">进入 →</span>
      </router-link>
    </section>
  </div>
</template>

<script setup>
const games = [
  {
    to: '/app/arcade/schulte',
    glyph: '#',
    name: '舒尔特方格',
    tag: '注意力 · 视觉搜索',
    desc: '按 1 到 N² 的顺序快速点击，经典的专注力训练。',
  },
  {
    to: '/app/arcade/stroop',
    glyph: '◑',
    name: '斯特鲁普测试',
    tag: '认知冲突 · 反应力',
    desc: '选“字的颜色”而不是字义 —— 大脑会不听使唤地卡壳。',
  },
  {
    to: '/app/arcade/dots',
    glyph: '⁙',
    name: '点位序列记忆',
    tag: '空间 · 工作记忆',
    desc: '记住格子亮起的顺序，再一个个复现出来。',
  },
  {
    to: '/app/arcade/reaction',
    glyph: '⚡',
    name: '反应速度测试',
    tag: '反应力 · 毫秒',
    desc: '看到绿色立刻点，测你从看到到动手的纯反应时间。',
  },
  {
    to: '/app/arcade/size',
    glyph: '⧉',
    name: '数值·字号冲突',
    tag: '认知冲突 · 数字',
    desc: '选数值大的那个 —— 但字号偏偏反着来忽悠你。',
  },
]
</script>

<style scoped>
.arcade-hero {
  text-align: left;
}

.arcade-title {
  font-family: var(--mono);
  font-size: clamp(1.5rem, 4vw, 2.1rem);
  margin: 0.35rem 0 0.5rem;
}

.arcade-lead {
  color: var(--text-muted);
  line-height: 1.7;
  margin: 0;
  max-width: 46rem;
}

.arcade-lead strong {
  color: var(--orange);
}

.arcade-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.arcade-game-card {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  text-decoration: none;
  color: inherit;
  position: relative;
  overflow: hidden;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.arcade-game-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 60%, color-mix(in srgb, var(--orange) 10%, transparent));
  opacity: 0;
  transition: opacity 0.18s ease;
  pointer-events: none;
}

.arcade-game-card:hover {
  transform: translateY(-3px);
  border-color: color-mix(in srgb, var(--orange) 45%, var(--border));
  box-shadow: 0 8px 22px color-mix(in srgb, var(--text) 10%, transparent);
}

.arcade-game-card:hover::after {
  opacity: 1;
}

.arcade-game-glyph {
  font-family: var(--mono);
  font-size: 2rem;
  line-height: 1;
  color: var(--orange);
}

.arcade-game-name {
  font-family: var(--mono);
  font-size: 1.15rem;
  margin: 0;
}

.arcade-game-tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 0;
}

.arcade-game-desc {
  color: var(--text-muted);
  font-size: 0.85rem;
  line-height: 1.6;
  margin: 0.15rem 0 0;
}

.arcade-game-go {
  font-family: var(--mono);
  font-size: 0.76rem;
  color: var(--orange);
  margin-top: auto;
  padding-top: 0.5rem;
}
</style>