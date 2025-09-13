<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>JouleJournal Login</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                label="Username"
                v-model="username"
                prepend-icon="mdi-account"
                type="text"
                required
              ></v-text-field>
              <v-text-field
                label="Password"
                v-model="password"
                prepend-icon="mdi-lock"
                type="password"
                required
              ></v-text-field>
              <v-alert v-if="error" type="error" dense>
                Login failed. Please check your credentials.
              </v-alert>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="handleLogin">Login</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('admin')
const password = ref('admin')
const error = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  error.value = false
  const success = await authStore.login(username.value, password.value)
  if (success) {
    router.push('/')
  } else {
    error.value = true
  }
}
</script>
