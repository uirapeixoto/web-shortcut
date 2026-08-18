<template>
  <li class="tree-node">
    <div
      v-if="node.type === 'dir'"
      class="tree-row tree-row--dir"
      @click="expanded = !expanded"
    >
      <svg class="tree-chevron" :class="{ open: expanded }" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="9 18 15 12 9 6"/></svg>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
      <span class="tree-label">{{ node.name }}</span>
    </div>
    <div
      v-else
      class="tree-row tree-row--file"
      :class="{ active: node.path === activePath }"
      @click="$emit('open-file', node.path)"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <span class="tree-label">{{ node.name }}</span>
    </div>

    <ul v-if="node.type === 'dir' && expanded" class="tree-children">
      <DocTreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :active-path="activePath"
        @open-file="$emit('open-file', $event)"
      />
    </ul>
  </li>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  node: { type: Object, required: true },
  activePath: { type: String, default: '' },
})
defineEmits(['open-file'])

const expanded = ref(props.node.path === '' || (props.node.children?.length ?? 0) <= 12)
</script>

<style scoped>
.tree-node { list-style: none; }
.tree-children { padding-left: 14px; margin: 0; }

.tree-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
  color: var(--text2);
  user-select: none;
}
.tree-row:hover { background: rgba(99, 102, 241, 0.1); color: var(--text); }
.tree-row--file.active {
  background: rgba(99, 102, 241, 0.18);
  color: var(--text);
  font-weight: 600;
}
.tree-row--dir { color: var(--text); }

.tree-chevron {
  flex-shrink: 0;
  transition: transform 0.15s;
}
.tree-chevron.open { transform: rotate(90deg); }

.tree-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
