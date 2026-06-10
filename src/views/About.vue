<template>
  <div class="about">
    <NavBar />
    <main class="page-main">
      <div class="container layout-single">
        <div class="page-content">
          <h1 class="page-title">关于我</h1>

          <h2>Cyinc 的学习笔记</h2>
          <p>这个博客是我自己的知识库：前端、后端、Java，以及最近在学的 AI Agent。文章主要是写给自己看的，顺便公开出来。</p>

          <h3>现在在学什么</h3>
          <p>重心从前端框架转向了 Agent 开发——怎么设计工具调用、怎么搭 RAG、怎么用 Cursor SDK 做自动化。Rhino / 3D 相关的旧笔记还留在归档里，但已经不是主线了。</p>

          <blockquote>"写下来，才算真正学过一遍。"</blockquote>

          <h3>技术栈</h3>
          <div class="skill-tags" style="margin-bottom:1.5rem">
            <span>Vue / JS</span>
            <span>Agent</span>
            <span>Python</span>
            <span>Node.js</span>
            <span>Java</span>
            <span>PHP</span>
          </div>

          <h3>联系方式</h3>
          <p>📧 邮箱：<a href="mailto:1344908013@qq.com">1344908013@qq.com</a></p>
          <p>🌐 博客：<a href="https://cyinc.github.io">https://cyinc.github.io</a></p>
        </div>
      </div>
    </main>
    <MusicPlayer />
  </div>
</template>

<script setup>
import NavBar from '../components/NavBar.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
</script>
