/**
 * SISTEMA DE INVENTÁRIO MMORPG
 * JavaScript - Lógica de Interação e Drag & Drop
 */

// ============================================
// ESTADO GLOBAL
// ============================================

const APP = {
    playerID: 1,
    selectedItem: null,
    libraryOpen: false,
    tooltipData: {},
    draggedFrom: null,
    draggedItemId: null,
    currentBagItemId: null,
    draggedBagSlotIndex: null,
    draggedBagItemId: null,
    contextItemId: null,
    contextBagSlotIndex: null,
    inventoryEditItemId: null,
};

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Iniciando Sistema de Inventário MMORPG');

    // Inicializa drag & drop
    initSortable();

    // Inicializa eventos
    initEvents();

    // Carrega dados
    loadPlayerData();

    console.log('✅ Sistema inicializado');
});

// ============================================
// DRAG & DROP COM SORTABLEJS
// ============================================

function initSortable() {
    // Bolsa selecionada
    const bagGrid = document.querySelector('.bag-items-grid');
    if (bagGrid) {
        Sortable.create(bagGrid, {
            group: {
                name: 'inventory',
                pull: true,
                put: ['inventory', 'library', 'equipment']
            },
            animation: 150,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onStart: (evt) => {
                const item = evt.item;
                APP.draggedFrom = 'bag';
                APP.draggedItemId = item.dataset.itemId;
                item.classList.add('dragging');
            },
            onAdd: (evt) => {
                const fromId = evt.from?.id;
                const itemId = evt.item?.dataset?.itemId;
                const bagItemId = getCurrentBagItemId();

                if (fromId === 'library-items') {
                    createItemFromLibrary(itemId, bagItemId);
                    evt.item.remove();
                    return;
                }

                if (evt.from?.classList?.contains('equipment-slot')) {
                    unequipItem(itemId, bagItemId);
                    evt.item.remove();
                    return;
                }
            },
            onEnd: (evt) => {
                const item = evt.item;
                item.classList.remove('dragging');
                APP.draggedFrom = null;
                APP.draggedItemId = null;
            }
        });
    }

    // Slots de equipamento
    const equipmentSlots = document.querySelectorAll('.equipment-slot');
    equipmentSlots.forEach(slot => {
        Sortable.create(slot, {
            group: {
                name: 'equipment',
                pull: true,
                put: (to, from, item) => {
                    if (from?.id === 'library-items') return true;
                    if (to?.dataset?.locked === 'true') return false;
                    return true;
                }
            },
            animation: 150,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onStart: (evt) => {
                APP.draggedFrom = 'equipment';
                APP.draggedItemId = evt.item?.dataset?.itemId || null;
            },
            onAdd: (evt) => {
                const itemId = evt.item?.dataset?.itemId;
                if (!itemId) return;
                const slotId = evt.to.dataset.slotId;
                if (evt.from?.id === 'library-items') {
                    showNotification('❌ Adicione o item a uma bolsa antes de equipar', 'error');
                    evt.item.remove();
                    return;
                }
                equipItem(itemId, slotId);
            },
            onEnd: () => {
                APP.draggedFrom = null;
                APP.draggedItemId = null;
            }
        });
    });

    // Biblioteca (drag para copiar ate bag)
    const libraryItems = document.getElementById('library-items');
    if (libraryItems) {
        Sortable.create(libraryItems, {
            group: {
                name: 'library',
                pull: 'clone',
                put: false
            },
            sort: false,
            animation: 150,
            ghostClass: 'sortable-ghost',
            onStart: (evt) => {
                APP.draggedFrom = 'library';
                APP.draggedItemId = evt.item?.dataset?.itemId || null;
            },
            onEnd: () => {
                APP.draggedFrom = null;
                APP.draggedItemId = null;
            },
        });
    }
}

// ============================================
// VALIDAÇÕES
// ============================================

function validateItemTypeForSlot(item, slot) {
    const itemType = item.dataset?.itemType;
    const slotType = slot.dataset?.slotType;
    const slotName = slot.dataset?.slotName;

    if (!itemType || !slotType) return false;

    if (itemType === 'consumable') return false;

    if (slotType === 'weapon') {
        if (itemType === 'shield') return slotName === 'Arma 2';
        return ['sword', 'axe', 'dagger', 'bow'].includes(itemType);
    }

    return itemType === slotType;
}

// ============================================
// OPERAÇÕES DE ITEM - AJAX
// ============================================

async function moveItemBetweenBags(itemId, sourceBagItemId, targetBagItemId) {
    try {
        const response = await fetch('/api/inventory/move-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                source_bag_item_id: parseInt(sourceBagItemId),
                target_bag_item_id: parseInt(targetBagItemId),
            })
        });

        const result = await response.json();

        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao mover item'), 'error');
            location.reload(); // Recarga para resetar estado visual
        } else {
            showNotification('✅ Item movido com sucesso', 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao mover item', 'error');
    }
}

async function moveBagSlot(sourceSlotIndex, targetSlotIndex) {
    try {
        const response = await fetch('/api/inventory/move-bag-slot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source_slot_index: parseInt(sourceSlotIndex),
                target_slot_index: parseInt(targetSlotIndex),
            })
        });

        const result = await response.json();

        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao mover bolsa'), 'error');
            location.reload();
        } else {
            showNotification('🎒 Bolsa movida!', 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao mover bolsa', 'error');
    }
}

async function equipBagInSlot(itemId, slotIndex) {
    try {
        const response = await fetch('/api/inventory/equip-bag', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                slot_index: parseInt(slotIndex),
            })
        });

        const result = await response.json();

        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao equipar bolsa'), 'error');
            location.reload();
        } else {
            showNotification('🎒 Bolsa equipada!', 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao equipar bolsa', 'error');
    }
}

async function equipItem(itemId, slotId) {
    try {
        const response = await fetch('/equipment/equip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                slot_id: parseInt(slotId),
            })
        });

        const result = await response.json();

        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao equipar'), 'error');
            location.reload();
        } else {
            showNotification('⚔️ Item equipado!', 'success');
            updateEquipmentUI(result);
            updateStats();
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao equipar', 'error');
    }
}

async function unequipItem(itemId, targetBagItemId) {
    try {
        const response = await fetch('/equipment/unequip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                target_bag_item_id: targetBagItemId ? parseInt(targetBagItemId) : null,
            })
        });

        const result = await response.json();

        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao desequipar'), 'error');
            location.reload();
        } else {
            showNotification('📦 Item desequipado!', 'success');
            updateEquipmentUI(result);
            updateStats();
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao desequipar', 'error');
    }
}

async function createItemFromLibrary(itemId, bagItemId) {
    if (!bagItemId) {
        showNotification('❌ Selecione uma bolsa primeiro', 'error');
        return;
    }
    try {
        const response = await fetch('/api/inventory/create-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                bag_item_id: parseInt(bagItemId),
            })
        });

        const result = await response.json();

        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao criar item'), 'error');
        } else {
            showNotification('✅ Item adicionado ao inventário!', 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao criar item', 'error');
    }
}

// ============================================
// TOOLTIPS
// ============================================

function initTooltip() {
    document.addEventListener('mouseover', (e) => {
        const item = e.target.closest('.inventory-slot, .equipped-item, .library-item');

        if (!item) {
            hideTooltip();
            return;
        }

        showTooltip(item, e);
    });

    document.addEventListener('mouseout', (e) => {
        if (!e.target.closest('.tooltip')) {
            hideTooltip();
        }
    });

    document.addEventListener('mousemove', (e) => {
        const tooltip = document.getElementById('tooltip');
        if (tooltip.classList.contains('active')) {
            updateTooltipPosition(e.clientX, e.clientY);
        }
    });
}

function showTooltip(element, event) {
    const itemId = element.dataset.itemId;
    const itemName = element.querySelector('.item-name')?.textContent ||
        element.querySelector('.library-item-name')?.textContent ||
        element.title;

    if (!itemId && !itemName) return;

    const tooltip = document.getElementById('tooltip');

    // Monta conteúdo
    let content = `<div class="tooltip-title">${itemName}</div>`;

    const rawStats = element.dataset.itemStats;
    if (rawStats) {
        try {
            const stats = JSON.parse(rawStats);
            Object.entries(stats).forEach(([key, value]) => {
                content += `<div class="tooltip-stat"><span class="tooltip-stat-label">${key}</span><span class="tooltip-stat-value">${value}</span></div>`;
            });
        } catch (error) {
            // Ignora stats invalidos
        }
    } else {
        const statsElement = element.querySelector('.library-item-stats');
        if (statsElement) {
            const stats = statsElement.querySelectorAll('.stat-tag');
            stats.forEach(stat => {
                content += `<div class="tooltip-stat">${stat.textContent}</div>`;
            });
        }
    }

    tooltip.innerHTML = content;
    tooltip.classList.add('active');

    updateTooltipPosition(event.clientX, event.clientY);
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.classList.remove('active');
}

function updateTooltipPosition(x, y) {
    const tooltip = document.getElementById('tooltip');
    const offset = 10;

    // Posiciona com alguns pixels de offset
    tooltip.style.left = (x + offset) + 'px';
    tooltip.style.top = (y + offset) + 'px';

    // Verifica se sai da tela
    const rect = tooltip.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
        tooltip.style.left = (window.innerWidth - rect.width - 10) + 'px';
    }
    if (rect.bottom > window.innerHeight) {
        tooltip.style.top = (window.innerHeight - rect.height - 10) + 'px';
    }
}

// ============================================
// EVENTOS
// ============================================

function initEvents() {
    // Biblioteca
    document.getElementById('btn-library')?.addEventListener('click', toggleLibrary);
    document.getElementById('btn-close-library')?.addEventListener('click', closeLibrary);
    document.getElementById('btn-stats')?.addEventListener('click', showStats);
    document.getElementById('btn-items')?.addEventListener('click', openItemsModal);
    document.getElementById('btn-close-items')?.addEventListener('click', closeItemsModal);

    // Tooltips
    initTooltip();

    // Drag modal biblioteca
    initModalDrag();

    // Bag slots
    initBagSlots();

    // Context menu
    initContextMenu();

    // CRUD itens
    initItemsCrud();

    // Busca biblioteca
    document.getElementById('search-library')?.addEventListener('input', debounce(() => {
        filterLibrary();
    }, 300));

    document.getElementById('filter-type')?.addEventListener('change', filterLibrary);

    // Organizar bolsa
    window.organizeBag = organizeBag;
}

function toggleLibrary() {
    const modal = document.getElementById('library-modal');

    if (modal.classList.contains('active')) {
        closeLibrary();
    } else {
        openLibrary();
    }
}

function openLibrary() {
    const modal = document.getElementById('library-modal');
    modal.classList.add('active');
    APP.libraryOpen = true;
}

function closeLibrary() {
    const modal = document.getElementById('library-modal');
    modal.classList.remove('active');
    APP.libraryOpen = false;
}

function showStats() {
    alert('Stats do set equipado:\n\n(Função a implementar com mais detalhe)');
}

// ============================================
// BOLSAS FIXAS
// ============================================

function initBagSlots() {
    const slots = document.querySelectorAll('.bag-slot');
    const activeSlot = document.querySelector('.bag-slot.active');
    if (activeSlot?.dataset?.bagItemId) {
        APP.currentBagItemId = parseInt(activeSlot.dataset.bagItemId);
    }

    slots.forEach(slot => {
        const hasBag = !!slot.dataset.bagItemId;
        slot.setAttribute('draggable', hasBag ? 'true' : 'false');

        slot.addEventListener('dragstart', (event) => {
            if (!slot.dataset.bagItemId) return;
            APP.draggedFrom = 'bag-slot';
            APP.draggedBagSlotIndex = slot.dataset.slotIndex;
            APP.draggedBagItemId = slot.dataset.bagItemId;
            APP.draggedItemId = slot.dataset.bagItemId;
            event.dataTransfer.setData('text/plain', slot.dataset.bagItemId);
        });

        slot.addEventListener('dragend', () => {
            if (APP.draggedFrom === 'bag-slot') {
                APP.draggedFrom = null;
                APP.draggedBagSlotIndex = null;
                APP.draggedBagItemId = null;
                APP.draggedItemId = null;
            }
        });

        slot.addEventListener('click', () => {
            const bagItemId = slot.dataset.bagItemId;
            if (!bagItemId) {
                showNotification('❌ Slot de bolsa vazio', 'error');
                return;
            }
            window.location.href = `/?bag_item_id=${bagItemId}`;
        });

        slot.addEventListener('dragover', (event) => {
            event.preventDefault();
            slot.classList.add('drag-over');
        });

        slot.addEventListener('dragleave', () => {
            slot.classList.remove('drag-over');
        });

        slot.addEventListener('drop', (event) => {
            event.preventDefault();
            slot.classList.remove('drag-over');

            const targetBagItemId = slot.dataset.bagItemId;
            const targetSlotIndex = slot.dataset.slotIndex;

            if (!APP.draggedItemId) return;

            if (APP.draggedFrom === 'bag-slot') {
                if (!APP.draggedBagSlotIndex || !targetSlotIndex) return;
                moveBagSlot(parseInt(APP.draggedBagSlotIndex), parseInt(targetSlotIndex));
                return;
            }

            if (APP.draggedFrom === 'library') {
                if (!targetSlotIndex) return;
                equipBagInSlot(APP.draggedItemId, targetSlotIndex);
                return;
            }

            if (APP.draggedFrom === 'bag') {
                if (!targetBagItemId) {
                    showNotification('❌ Slot de bolsa vazio', 'error');
                    return;
                }
                const sourceBagItemId = getCurrentBagItemId();
                if (!sourceBagItemId || sourceBagItemId === targetBagItemId) return;
                moveItemBetweenBags(APP.draggedItemId, sourceBagItemId, targetBagItemId);
                return;
            }

            if (APP.draggedFrom === 'equipment') {
                if (!targetBagItemId) {
                    showNotification('❌ Slot de bolsa vazio', 'error');
                    return;
                }
                unequipItem(APP.draggedItemId, parseInt(targetBagItemId));
            }
        });
    });
}

// ============================================
// CONTEXT MENU (ITEMS)
// ============================================

function initContextMenu() {
    const menu = document.getElementById('context-menu');
    if (!menu) return;

    // Eventos para itens no inventário
    document.addEventListener('contextmenu', (event) => {
        const item = event.target.closest('.inventory-slot.item-slot');
        if (item) {
            event.preventDefault();
            APP.contextItemId = item.dataset.itemId;
            APP.contextBagSlotIndex = null;
            openContextMenu(event.clientX, event.clientY);
            return;
        }

        // Eventos para bolsas equipadas (bag-slot)
        const bagSlot = event.target.closest('.bag-slot');
        if (bagSlot && bagSlot.dataset.bagItemId) {
            event.preventDefault();
            APP.contextBagSlotIndex = parseInt(bagSlot.dataset.slotIndex);
            APP.contextItemId = null;
            openContextMenu(event.clientX, event.clientY);
            return;
        }
    });

    document.addEventListener('click', (event) => {
        if (!menu.contains(event.target)) {
            closeContextMenu();
        }
    });

    menu.addEventListener('click', (event) => {
        const action = event.target.closest('[data-action]')?.dataset?.action;
        if (!action) return;
        handleContextMenuAction(action);
    });
}

function openContextMenu(x, y) {
    const menu = document.getElementById('context-menu');
    if (!menu) return;

    // Show/hide context menu buttons based on context type
    const isItemContext = APP.contextItemId !== null;
    const isBagContext = APP.contextBagSlotIndex !== null;

    menu.querySelectorAll('[data-context="item"]').forEach(btn => {
        btn.style.display = isItemContext ? 'block' : 'none';
    });

    menu.querySelectorAll('[data-context="bag"]').forEach(btn => {
        btn.style.display = isBagContext ? 'block' : 'none';
    });

    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.classList.add('active');
}

function closeContextMenu() {
    const menu = document.getElementById('context-menu');
    if (!menu) return;
    menu.classList.remove('active');
}

function handleContextMenuAction(action) {
    // Handle bag slot actions
    if (APP.contextBagSlotIndex !== null) {
        closeContextMenu();
        if (action === 'unequip') {
            if (confirm('Desequipar esta bolsa?')) {
                unequipBag(APP.contextBagSlotIndex);
            }
            return;
        }

        if (action === 'delete') {
            const bagItemId = document.querySelector(`.bag-slot[data-slot-index="${APP.contextBagSlotIndex}"]`)?.dataset?.bagItemId;
            if (bagItemId && confirm('Deletar esta bolsa? (Certifique-se de que está vazia)')) {
                deleteBag(bagItemId);
            }
            return;
        }
        return;
    }

    // Handle inventory item actions
    const itemId = APP.contextItemId;
    closeContextMenu();
    if (!itemId) return;

    if (action === 'edit') {
        openInventoryItemEditor(itemId);
        return;
    }

    if (action === 'delete') {
        if (confirm('Deseja excluir este item?')) {
            deleteInventoryItem(itemId);
        }
        return;
    }

    if (action === 'duplicate') {
        duplicateInventoryItem(itemId);
        return;
    }

    if (action === 'move') {
        moveInventoryItemToBag(itemId);
    }
}

// ============================================
// GERENCIAMENTO DE BOLSAS
// ============================================

async function unequipBag(slotIndex) {
    try {
        const response = await fetch('/api/inventory/unequip-bag', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slot_index: slotIndex })
        });
        const result = await response.json();
        if (result.success) {
            console.log('✅ Bolsa desequipada');
            location.reload();
        } else {
            alert(`Erro: ${result.error}`);
        }
    } catch (error) {
        console.error('Erro ao desequipar bolsa:', error);
        alert('Erro ao desequipar bolsa');
    }
}

async function deleteBag(bagItemId) {
    try {
        const response = await fetch(`/api/inventory/bags/${bagItemId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        if (result.success) {
            console.log('✅ Bolsa deletada');
            location.reload();
        } else {
            alert(`Erro: ${result.error}`);
        }
    } catch (error) {
        console.error('Erro ao deletar bolsa:', error);
        alert('Erro ao deletar bolsa');
    }
}

// ============================================
// CRUD DE ITENS
// ============================================

function openItemsModal() {
    document.getElementById('items-modal')?.classList.add('active');
}

function closeItemsModal() {
    document.getElementById('items-modal')?.classList.remove('active');
}

function initItemsCrud() {
    const list = document.getElementById('items-list');
    const btnSave = document.getElementById('btn-item-save');
    const btnNew = document.getElementById('btn-item-new');
    const btnDelete = document.getElementById('btn-item-delete');

    list?.addEventListener('click', (event) => {
        const editBtn = event.target.closest('.btn-edit');
        const deleteBtn = event.target.closest('.btn-danger');

        if (editBtn) {
            const itemId = editBtn.dataset.itemId;
            loadItemIntoForm(itemId);
        }

        if (deleteBtn) {
            const itemId = deleteBtn.dataset.itemId;
            deleteLibraryItem(itemId);
        }
    });

    btnSave?.addEventListener('click', (event) => {
        event.preventDefault();
        saveLibraryItem();
    });

    btnNew?.addEventListener('click', (event) => {
        event.preventDefault();
        resetItemForm();
    });

    btnDelete?.addEventListener('click', (event) => {
        event.preventDefault();
        const itemId = document.getElementById('item-id')?.value;
        if (itemId) deleteLibraryItem(itemId);
    });
}

function getItemFormPayload() {
    return {
        name: document.getElementById('item-name')?.value || '',
        item_type: document.getElementById('item-type')?.value || '',
        weight: document.getElementById('item-weight')?.value || 0,
        rarity: document.getElementById('item-rarity')?.value || 'common',
        data: document.getElementById('item-data')?.value || ''
    };
}

function resetItemForm() {
    document.getElementById('item-id').value = '';
    document.getElementById('item-name').value = '';
    document.getElementById('item-type').value = 'helmet';
    document.getElementById('item-weight').value = '';
    document.getElementById('item-rarity').value = 'common';
    document.getElementById('item-data').value = '';
    APP.inventoryEditItemId = null;
}

async function saveLibraryItem() {
    const itemId = document.getElementById('item-id')?.value;
    const payload = getItemFormPayload();

    if (APP.inventoryEditItemId) {
        await updateInventoryItem(APP.inventoryEditItemId, payload);
        return;
    }

    try {
        const response = await fetch(itemId ? `/api/items/${itemId}` : '/api/items', {
            method: itemId ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao salvar item'), 'error');
            return;
        }

        showNotification('✅ Item salvo', 'success');
        resetItemForm();
        refreshLibrary();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao salvar item', 'error');
    }
}

async function openInventoryItemEditor(itemId) {
    try {
        const response = await fetch(`/api/inventory/items/${itemId}`);
        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao carregar item'), 'error');
            return;
        }

        const item = result.item;
        APP.inventoryEditItemId = item.id;

        document.getElementById('item-id').value = item.id;
        document.getElementById('item-name').value = item.name || '';
        document.getElementById('item-type').value = item.item_type || 'helmet';
        document.getElementById('item-weight').value = item.weight || 0;
        document.getElementById('item-rarity').value = item.rarity || 'common';
        document.getElementById('item-data').value = JSON.stringify(item.stats || {}, null, 2);

        openItemsModal();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao carregar item', 'error');
    }
}

async function updateInventoryItem(itemId, payload) {
    try {
        const response = await fetch(`/api/inventory/items/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao salvar item'), 'error');
            return;
        }
        showNotification('✅ Item atualizado', 'success');
        resetItemForm();
        location.reload();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao salvar item', 'error');
    }
}

async function deleteInventoryItem(itemId) {
    try {
        const response = await fetch(`/api/inventory/items/${itemId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao excluir item'), 'error');
            return;
        }
        showNotification('🗑️ Item excluido', 'success');
        location.reload();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao excluir item', 'error');
    }
}

async function duplicateInventoryItem(itemId) {
    try {
        const response = await fetch(`/api/inventory/items/${itemId}/duplicate`, {
            method: 'POST'
        });
        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao duplicar item'), 'error');
            return;
        }
        showNotification('✅ Item duplicado', 'success');
        location.reload();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao duplicar item', 'error');
    }
}

function getEquippedBagItemIdBySlot(slotIndex) {
    const slot = document.querySelector(`.bag-slot[data-slot-index="${slotIndex}"]`);
    const bagItemId = slot?.dataset?.bagItemId;
    return bagItemId ? parseInt(bagItemId) : null;
}

async function moveInventoryItemToBag(itemId) {
    const input = prompt('Mover para slot de bolsa (1-6):');
    if (!input) return;
    const slotNumber = parseInt(input, 10);
    if (Number.isNaN(slotNumber) || slotNumber < 1 || slotNumber > 6) {
        showNotification('❌ Slot invalido', 'error');
        return;
    }
    const bagItemId = getEquippedBagItemIdBySlot(slotNumber - 1);
    if (!bagItemId) {
        showNotification('❌ Slot de bolsa vazio', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/inventory/items/${itemId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_bag_item_id: bagItemId })
        });
        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao mover item'), 'error');
            return;
        }
        showNotification('✅ Item movido', 'success');
        location.reload();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao mover item', 'error');
    }
}

async function deleteLibraryItem(itemId) {
    try {
        const response = await fetch(`/api/items/${itemId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (!result.success) {
            showNotification('❌ ' + (result.error || 'Erro ao excluir item'), 'error');
            return;
        }
        showNotification('🗑️ Item excluido', 'success');
        resetItemForm();
        refreshLibrary();
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao excluir item', 'error');
    }
}

function loadItemIntoForm(itemId) {
    const row = document.querySelector(`.items-list-row[data-item-id="${itemId}"]`);
    if (!row) return;

    const name = row.querySelector('.items-list-name')?.textContent || '';
    const type = row.dataset.itemType || row.querySelector('.items-list-type')?.textContent || '';
    const weight = row.dataset.itemWeight || '';
    const rarity = row.dataset.itemRarity || 'common';
    const stats = row.dataset.itemStats || '';

    document.getElementById('item-id').value = itemId;
    document.getElementById('item-name').value = name;
    document.getElementById('item-type').value = type;
    document.getElementById('item-weight').value = weight;
    document.getElementById('item-rarity').value = rarity;
    if (stats) {
        try {
            document.getElementById('item-data').value = JSON.stringify(JSON.parse(stats), null, 2);
        } catch (error) {
            document.getElementById('item-data').value = stats;
        }
    } else {
        document.getElementById('item-data').value = '';
    }
}

// ============================================
// BIBLIOTECA
// ============================================

async function filterLibrary() {
    const search = document.getElementById('search-library')?.value || '';
    const type = document.getElementById('filter-type')?.value || '';

    try {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (type) params.append('type', type);

        const response = await fetch(`/api/library/search?${params}`);
        const result = await response.json();

        if (result.success) {
            updateLibraryDisplay(result.items);
            updateItemsList(result.items);
        }
    } catch (error) {
        console.error('Erro ao filtrar biblioteca:', error);
    }
}

function refreshLibrary() {
    const search = document.getElementById('search-library')?.value || '';
    const type = document.getElementById('filter-type')?.value || '';
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (type) params.append('type', type);

    fetch(`/api/library/search?${params}`)
        .then(r => r.json())
        .then(result => {
            if (result.success) {
                updateLibraryDisplay(result.items);
                updateItemsList(result.items);
            }
        })
        .catch(err => console.error('Erro ao atualizar biblioteca:', err));
}

function updateLibraryDisplay(items) {
    const container = document.getElementById('library-items');
    container.innerHTML = '';

    items.forEach(item => {
        const stats = item.stats || {};
        const statTags = Object.entries(stats)
            .map(([key, value]) => `<span class="stat-tag">+${value} ${key}</span>`)
            .join('');
        const html = `
            <div class="library-item" 
                 data-item-id="${item.id}"
                 data-item-type="${item.item_type}"
                 data-item-stats='${JSON.stringify(stats)}'
                 data-rarity="${item.rarity}"
                 onclick="createItemFromLibrary(${item.id}, getCurrentBagItemId())">
                <div class="library-item-header" style="border-left: 4px solid ${item.rarity_color}">
                    <span class="library-item-name">${item.name}</span>
                    <span class="library-item-rarity">${item.rarity.toUpperCase()}</span>
                </div>
                <div class="library-item-details">
                    <span>🎒 ${item.weight}kg</span>
                    <span>${item.item_type}</span>
                </div>
                ${statTags ? `<div class="library-item-stats">${statTags}</div>` : ''}
            </div>
        `;
        container.innerHTML += html;
    });

    // Reinicializa Sortable
    Sortable.get(container)?.destroy();
    Sortable.create(container, {
        group: {
            name: 'library',
            pull: 'clone',
            put: false
        },
        sort: false,
        animation: 150,
    });
}

function updateItemsList(items) {
    const list = document.getElementById('items-list');
    if (!list) return;
    list.innerHTML = '';

    items.forEach(item => {
        const stats = item.stats || {};
        const row = document.createElement('div');
        row.className = 'items-list-row';
        row.dataset.itemId = item.id;
        row.dataset.itemType = item.item_type;
        row.dataset.itemWeight = item.weight;
        row.dataset.itemRarity = item.rarity;
        row.dataset.itemStats = JSON.stringify(stats);
        row.innerHTML = `
            <div class="items-list-info">
                <span class="items-list-name">${item.name}</span>
                <span class="items-list-type">${item.item_type}</span>
            </div>
            <div class="items-list-actions">
                <button class="btn btn-small btn-edit" data-item-id="${item.id}">Editar</button>
                <button class="btn btn-small btn-danger" data-item-id="${item.id}">Excluir</button>
            </div>
        `;
        list.appendChild(row);
    });
}

function getCurrentBagItemId() {
    const activeSlot = document.querySelector('.bag-slot.active');
    if (activeSlot?.dataset?.bagItemId) {
        return parseInt(activeSlot.dataset.bagItemId);
    }
    const bagGrid = document.querySelector('.bag-items-grid');
    if (bagGrid?.dataset?.bagItemId) {
        return parseInt(bagGrid.dataset.bagItemId);
    }
    return APP.currentBagItemId;
}

// ============================================
// MODAL DRAG
// ============================================

function initModalDrag() {
    const modal = document.getElementById('library-modal');
    const header = modal.querySelector('.modal-header');

    let isDragging = false;
    let startX, startY, startLeft, startTop;

    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        startLeft = modal.offsetLeft;
        startTop = modal.offsetTop;
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;

        const moveX = e.clientX - startX;
        const moveY = e.clientY - startY;

        modal.style.left = (startLeft + moveX) + 'px';
        modal.style.top = (startTop + moveY) + 'px';
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
}

// ============================================
// ORGANIZAR BOLSA
// ============================================

async function organizeBag(bagItemId) {
    try {
        const response = await fetch('/api/inventory/organize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                bag_item_id: parseInt(bagItemId),
            })
        });

        const result = await response.json();

        if (result.success) {
            showNotification('✅ Bolsa organizada!', 'success');
        } else {
            showNotification('❌ Erro ao organizar', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('❌ Erro ao organizar', 'error');
    }
}

// ============================================
// ATUALIZAÇÃO DA UI
// ============================================

function updateInventoryUI(data) {
    if (!data) return;

    // Atualiza slot onde veio
    if (data.source_bag) {
        updateBagDisplay(data.source_bag.id);
    }

    // Atualiza slot onde foi
    if (data.target_bag) {
        updateBagDisplay(data.target_bag.id);
    }
}

function updateEquipmentUI(data) {
    if (!data) return;
    location.reload(); // Por enquanto, recarrega (melhorar depois)
}

function updateBagDisplay(bagId) {
    // Recarrega dados (simplificado por enquanto)
    loadPlayerData();
}

function updateStats() {
    // Atualiza stats do set
    fetch('/api/stats/calculate')
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                updateStatsDisplay(data.stats);
            }
        })
        .catch(err => console.error('Erro ao atualizar stats:', err));
}

function updateStatsDisplay(stats) {
    if (!stats) return;
    const elements = document.querySelectorAll('[data-stat-key]');
    elements.forEach(el => {
        const key = el.dataset.statKey;
        if (key in stats) {
            el.textContent = stats[key];
        }
    });
}

// ============================================
// CARREGAR DADOS
// ============================================

async function loadPlayerData() {
    try {
        const response = await fetch('/api/player');
        const data = await response.json();

        console.log('Dados do jogador carregados:', data);
        // UI já foi renderizada no servidor, apenas validar
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    }
}

// ============================================
// NOTIFICAÇÕES
// ============================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#2d5016' : type === 'error' ? '#5a1a1a' : '#1a3a5a'};
        color: white;
        border: 2px solid ${type === 'success' ? '#4CAF50' : type === 'error' ? '#FF5252' : '#2196F3'};
        border-radius: 4px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================
// UTILITÁRIOS
// ============================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function allowDrop(event) {
    event.preventDefault();
}

console.log('✅ app.js carregado com sucesso');
