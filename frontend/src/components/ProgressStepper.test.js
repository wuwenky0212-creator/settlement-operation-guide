/**
 * ProgressStepper Component Test
 * 
 * This is a simple test file to verify the ProgressStepper component works correctly.
 * 
 * Test scenarios:
 * 1. Component renders with provided steps
 * 2. Step status classes are applied correctly
 * 3. Connector classes are applied based on step status
 * 4. Component handles empty steps array
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProgressStepper from './ProgressStepper.vue'

describe('ProgressStepper', () => {
  it('renders steps correctly', () => {
    const steps = [
      { label: '交易点', status: 'completed' },
      { label: '已证实', status: 'completed' },
      { label: '已记账', status: 'current' },
      { label: '已发报', status: 'pending' },
      { label: '已完成', status: 'pending' }
    ]

    const wrapper = mount(ProgressStepper, {
      props: { steps }
    })

    // Check if all steps are rendered
    const stepNodes = wrapper.findAll('.step-node')
    expect(stepNodes).toHaveLength(5)

    // Check if labels are correct
    expect(wrapper.text()).toContain('交易点')
    expect(wrapper.text()).toContain('已证实')
    expect(wrapper.text()).toContain('已记账')
    expect(wrapper.text()).toContain('已发报')
    expect(wrapper.text()).toContain('已完成')
  })

  it('applies correct status classes', () => {
    const steps = [
      { label: 'Step 1', status: 'completed' },
      { label: 'Step 2', status: 'current' },
      { label: 'Step 3', status: 'pending' },
      { label: 'Step 4', status: 'failed' }
    ]

    const wrapper = mount(ProgressStepper, {
      props: { steps }
    })

    const stepNodes = wrapper.findAll('.step-node')
    
    expect(stepNodes[0].classes()).toContain('step-completed')
    expect(stepNodes[1].classes()).toContain('step-current')
    expect(stepNodes[2].classes()).toContain('step-pending')
    expect(stepNodes[3].classes()).toContain('step-failed')
  })

  it('renders connectors between steps', () => {
    const steps = [
      { label: 'Step 1', status: 'completed' },
      { label: 'Step 2', status: 'completed' },
      { label: 'Step 3', status: 'current' }
    ]

    const wrapper = mount(ProgressStepper, {
      props: { steps }
    })

    // Should have 2 connectors for 3 steps
    const connectors = wrapper.findAll('.step-connector')
    expect(connectors).toHaveLength(2)
  })

  it('handles empty steps array', () => {
    const wrapper = mount(ProgressStepper, {
      props: { steps: [] }
    })

    const stepNodes = wrapper.findAll('.step-node')
    expect(stepNodes).toHaveLength(0)
  })
})
