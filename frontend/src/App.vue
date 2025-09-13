<template>
  <v-app>
    <v-navigation-drawer app permanent>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            JouleJournal
          </v-list-item-title>
          <v-list-item-subtitle>
            Energy Monitoring
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item prepend-icon="mdi-view-dashboard" title="Report View" to="/"></v-list-item>
        <v-list-item prepend-icon="mdi-cog" title="Admin: Tariffs" to="/admin/tariffs"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
  //
</script>
