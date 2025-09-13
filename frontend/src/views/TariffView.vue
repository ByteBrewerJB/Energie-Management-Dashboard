<template>
  <v-container>
    <v-card>
      <v-card-title>
        Tariff Management
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openCreateDialog">New Tariff</v-btn>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="tariffs"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="openEditDialog(item)">mdi-pencil</v-icon>
          <v-icon small @click="openDeleteDialog(item)">mdi-delete</v-icon>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog for Create/Edit -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ dialogTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-text-field v-model="editedItem.start_date" label="Start Date" type="date" required></v-text-field>
            <v-text-field v-model="editedItem.end_date" label="End Date" type="date" required></v-text-field>
            <v-text-field v-model.number="editedItem.purchase_low_eur_kwh" label="Purchase Low (€/kWh)" type="number" required></v-text-field>
            <v-text-field v-model.number="editedItem.purchase_high_eur_kwh" label="Purchase High (€/kWh)" type="number" required></v-text-field>
            <v-text-field v-model.number="editedItem.sale_eur_kwh" label="Sale (€/kWh)" type="number" required></v-text-field>
            <v-text-field v-model.number="editedItem.vat" label="VAT (%)" type="number" required></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDialog">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="saveItem">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog for Delete Confirmation -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Are you sure you want to delete this item?</v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDeleteDialog">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="deleteItemConfirm">OK</v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import apiClient from '@/api/axios'

const tariffs = ref([])
const loading = ref(true)
const dialog = ref(false)
const deleteDialog = ref(false)
const editedIndex = ref(-1)
const editedItem = ref({
  start_date: '',
  end_date: '',
  purchase_low_eur_kwh: 0,
  purchase_high_eur_kwh: 0,
  sale_eur_kwh: 0,
  vat: 0,
})
const defaultItem = { ...editedItem.value }

const headers = [
  { title: 'Start Date', value: 'start_date' },
  { title: 'End Date', value: 'end_date' },
  { title: 'Purchase Low (€/kWh)', value: 'purchase_low_eur_kwh' },
  { title: 'Purchase High (€/kWh)', value: 'purchase_high_eur_kwh' },
  { title: 'Sale (€/kWh)', value: 'sale_eur_kwh' },
  { title: 'VAT', value: 'vat' },
  { title: 'Actions', value: 'actions', sortable: false },
]

const dialogTitle = computed(() => (editedIndex.value === -1 ? 'New Tariff' : 'Edit Tariff'))

const fetchTariffs = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/api/tariffs/')
    tariffs.value = response.data
  } catch (error) {
    console.error('Failed to fetch tariffs:', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchTariffs)

const openCreateDialog = () => {
  editedItem.value = { ...defaultItem }
  editedIndex.value = -1
  dialog.value = true
}

const openEditDialog = (item) => {
  editedIndex.value = tariffs.value.indexOf(item)
  editedItem.value = { ...item }
  dialog.value = true
}

const openDeleteDialog = (item) => {
  editedIndex.value = tariffs.value.indexOf(item)
  editedItem.value = { ...item }
  deleteDialog.value = true
}

const closeDialog = () => {
  dialog.value = false
}

const closeDeleteDialog = () => {
  deleteDialog.value = false
}

const saveItem = async () => {
  if (editedIndex.value > -1) {
    // Update
    try {
      await apiClient.put(`/api/tariffs/${editedItem.value.id}`, editedItem.value)
      Object.assign(tariffs.value[editedIndex.value], editedItem.value)
    } catch (error) {
      console.error('Failed to update tariff:', error)
    }
  } else {
    // Create
    try {
      const response = await apiClient.post('/api/tariffs/', editedItem.value)
      tariffs.value.push(response.data)
    } catch (error) {
      console.error('Failed to create tariff:', error)
    }
  }
  closeDialog()
}

const deleteItemConfirm = async () => {
  try {
    await apiClient.delete(`/api/tariffs/${editedItem.value.id}`)
    tariffs.value.splice(editedIndex.value, 1)
  } catch (error) {
    console.error('Failed to delete tariff:', error)
  }
  closeDeleteDialog()
}
</script>
