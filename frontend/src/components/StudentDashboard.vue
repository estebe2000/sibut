<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Tableau de Bord Étudiant</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Radar Chart -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Progression Globale</h2>
          <div class="h-80">
            <RadarChart
              v-if="competencies.length > 0"
              :labels="competencies.map(c => c.name)"
              :dataset="competencies.map(c => c.progress)"
            />
            <div v-else class="flex justify-center items-center h-full text-gray-500">
                Chargement...
            </div>
          </div>
        </div>
      </div>

      <!-- Proof Upload -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Ajouter une Preuve au Portfolio</h2>
          <form @submit.prevent="uploadProof" class="space-y-4">
             <div class="form-control">
                <label class="label">Description</label>
                <input v-model="proofDesc" type="text" class="input input-bordered" placeholder="Ex: Rapport de stage" required />
             </div>
             <div class="form-control">
                <label class="label">Fichier</label>
                <input type="file" ref="fileInput" class="file-input file-input-bordered w-full" required />
             </div>
             <button type="submit" class="btn btn-primary" :disabled="uploading">
                {{ uploading ? 'Envoi...' : 'Envoyer' }}
             </button>
             <p v-if="uploadStatus" class="text-sm mt-2" :class="uploadStatus.type === 'success' ? 'text-success' : 'text-error'">
                {{ uploadStatus.message }}
             </p>
          </form>
        </div>
      </div>
    </div>

    <!-- Competency List -->
    <div class="mt-6">
        <h2 class="text-2xl font-bold mb-4">Détail des Compétences</h2>
        <div class="collapse collapse-arrow bg-base-100 border border-base-300 mb-2" v-for="comp in competencies" :key="comp.short_code">
            <input type="radio" name="my-accordion-2" />
            <div class="collapse-title text-xl font-medium flex justify-between">
                <span>{{ comp.short_code }} - {{ comp.name }}</span>
                <progress class="progress progress-primary w-56 mt-2" :value="comp.progress" max="100"></progress>
            </div>
            <div class="collapse-content">
                <p>Progression: {{ comp.progress.toFixed(0) }}%</p>
                <!-- ACs list would go here -->
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import RadarChart from './RadarChart.vue'

// Mock Data for now
const competencies = ref([])
const proofDesc = ref('')
const fileInput = ref(null)
const uploading = ref(false)
const uploadStatus = ref(null)

// TODO: Replace with real API calls using fetch or axios
onMounted(async () => {
    // Mocking API response for Dashboard
    // In real app: fetch(`/api/student/${user.id}/dashboard`)
    setTimeout(() => {
        competencies.value = [
            { short_code: 'C1', name: 'Marketing', progress: 40 },
            { short_code: 'C2', name: 'Vente', progress: 65 },
            { short_code: 'C3', name: 'Com', progress: 20 },
            { short_code: 'C4', name: 'Management', progress: 50 },
            { short_code: 'C5', name: 'Retail', progress: 80 },
        ]
    }, 500)
})

const uploadProof = async () => {
    if (!fileInput.value.files[0]) return

    uploading.value = true
    const formData = new FormData()
    formData.append('file', fileInput.value.files[0])
    formData.append('description', proofDesc.value)

    try {
        // Mock API call
        // const res = await fetch('/api/proofs/upload', { method: 'POST', body: formData })
        await new Promise(r => setTimeout(r, 1000)) // Sim delay

        uploadStatus.value = { type: 'success', message: 'Preuve ajoutée avec succès !' }
        proofDesc.value = ''
        fileInput.value.value = null
    } catch (e) {
        uploadStatus.value = { type: 'error', message: 'Erreur lors de l\'envoi.' }
    } finally {
        uploading.value = false
    }
}
</script>
