<template>
  <div class="home">
    <h1>操作指导系统</h1>
    <p>Settlement Operation Guide System</p>
    
    <div class="navigation">
      <router-link to="/transactions" class="nav-card">
        <h2>交易汇总查询</h2>
        <p>查询和管理交易确认书</p>
      </router-link>
      
      <router-link to="/cash-flows" class="nav-card">
        <h2>现金流查询</h2>
        <p>查询和跟踪现金流收付进度</p>
      </router-link>
      
      <router-link to="/demo" class="nav-card">
        <h2>组件演示</h2>
        <p>查看UI组件示例</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
// Home view component
</script>

<style scoped>
.home {
  padding: 2rem;
  text-align: center;
}

h1 {
  color: #D32F2F;
  margin-bottom: 1rem;
}

.navigation {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 3rem auto;
  padding: 0 2rem;
}

.nav-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  color: inherit;
  transition: all 0.3s;
}

.nav-card:hover {
  box-shadow: 0 4px 16px rgba(211, 47, 47, 0.2);
  transform: translateY(-4px);
}

.nav-card h2 {
  color: #D32F2F;
  margin-bottom: 0.5rem;
  font-size: 1.25rem;
}

.nav-card p {
  color: #666;
  font-size: 0.875rem;
}
</style>
