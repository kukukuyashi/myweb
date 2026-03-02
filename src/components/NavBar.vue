<template>
  <header class="navbar">
    <div class="header-content">
      <div class="logo">
        <span>Cyinc的个人博客</span>
      </div>
      <nav>
        <ul>
          <li><router-link to="/" class="nav-link" data-icon="🏠">首页</router-link></li>
          <li><router-link to="/about" class="nav-link" data-icon="ℹ️">关于</router-link></li>
          <li><router-link to="/archive" class="nav-link" data-icon="📚">归档</router-link></li>
          <li><router-link to="/music" class="nav-link" data-icon="🎵">音乐室</router-link></li>
          <li><router-link to="/guestbook" class="nav-link" data-icon="💬">留言板</router-link></li>
        </ul>
      </nav>
      <div class="nav-buttons">
        <button @click="toggleDarkMode" class="nav-btn dark-mode-btn" title="切换深色模式">
          {{ isDarkMode ? '🌞' : '🌙' }}
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 深色模式状态
const isDarkMode = ref(false)

// 切换深色模式
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
    localStorage.setItem('theme', 'light')
  }
}

// 初始化深色模式状态
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDarkMode.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  width: var(--sidebar-width);
  min-height: 100vh;
  padding: 2rem 0;
  box-shadow: 2px 0 15px rgba(0,0,0,0.12);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1002;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border-right: 3px solid rgba(255,255,255,0.1);
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('../../img/5.jpg') center/cover no-repeat;
  opacity: 0.1;
  z-index: -1;
  mix-blend-mode: overlay;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 1.5rem;
  flex-grow: 1;
  overflow: hidden;
  transition: opacity 0.3s ease;
  justify-content: flex-start;
  width: 100%;
}

.logo {
  font-weight: bold;
  letter-spacing: 1px;
  text-align: center;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  position: relative;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  width: 100%;
}

.logo span {
  color: #ffffff;
  font-weight: 600;
  display: inline-block;
  transition: all 0.3s ease;
}

.logo:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.logo:hover span {
  transform: scale(1.05);
  color: var(--primary-lighter);
}

nav {
  width: 100%;
}

nav ul {
  display: flex;
  flex-direction: column;
  list-style: none;
  gap: 1rem;
  width: 100%;
  padding: 0;
  margin: 0;
}

nav li {
  width: 100%;
}

nav a {
  width: 100%;
  display: block;
  text-align: center;
  padding: 0.75rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  text-decoration: none;
  font-weight: 500;
  position: relative;
}

nav a:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

nav a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 0;
  height: 2px;
  background: white;
  transition: width 0.3s ease;
}

nav a:hover::after {
  width: 100%;
}

.router-link-active {
  background: rgba(255,255,255,0.2) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 导航按钮样式 */
.nav-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 3rem;
  width: 100%;
  padding: 0 1.5rem;
  flex-direction: column;
}

.nav-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  font-size: 1.3rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.nav-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.nav-btn:hover::before {
  left: 100%;
}

.nav-btn:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.1) 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
  border-color: rgba(255,255,255,0.3);
}

.nav-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.dark-mode-btn {
  font-size: 1.5rem;
}

/* 深色模式样式 */
[data-theme="dark"] .navbar {
  background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
  border-right-color: rgba(255,255,255,0.05);
}

[data-theme="dark"] .navbar::before {
  opacity: 0.05;
}

[data-theme="dark"] .logo {
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .logo:hover {
  background: rgba(255,255,255,0.1);
}

[data-theme="dark"] nav a {
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] nav a:hover {
  background: rgba(255,255,255,0.1);
}

[data-theme="dark"] .nav-btn {
  background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
  border-color: rgba(255,255,255,0.1);
}

[data-theme="dark"] .nav-btn:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
  border-color: rgba(255,255,255,0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    width: 100%;
    min-height: auto;
    position: relative;
    padding: 1rem 0;
  }
  
  .header-content {
    flex-direction: column;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
  }
  
  nav ul {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  
  nav a {
    padding: 5px 10px;
    font-size: 1rem;
  }
  
  .nav-buttons {
    flex-direction: row;
    gap: 1rem;
    margin-top: 1rem;
    padding: 0 1rem;
  }
  
  .nav-btn {
    padding: 0.75rem 1rem;
    font-size: 1.1rem;
    flex: 1;
  }
  
  .dark-mode-btn {
    font-size: 1.3rem;
  }
  
  .hide-nav-btn {
    font-size: 1.1rem;
  }
}
</style>