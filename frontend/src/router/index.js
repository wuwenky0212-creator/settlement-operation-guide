import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/transactions'
    },
    {
      path: '/transactions',
      name: 'transaction-summary',
      component: () => import('../views/TransactionSummaryNew.vue')
    },
    {
      path: '/transactions/:externalId',
      name: 'transaction-detail',
      component: () => import('../views/TransactionDetail.vue')
    },
    {
      path: '/cash-flows',
      name: 'cash-flow-summary',
      component: () => import('../views/CashFlowSummary.vue')
    },
    {
      path: '/cash-flows/:cashFlowId',
      name: 'cash-flow-detail',
      component: () => import('../views/CashFlowDetail.vue')
    }
  ]
})

export default router
