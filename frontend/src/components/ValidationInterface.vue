<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Interface de Validation (Enseignant)</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Student Selection -->
        <div class="col-span-1 card bg-base-100 shadow-xl">
            <div class="card-body">
                <h2 class="card-title">Sélection</h2>
                <select class="select select-bordered w-full">
                    <option disabled selected>Choisir une activité</option>
                    <option>SAÉ 1.01</option>
                    <option>SAÉ 1.02</option>
                </select>
                <select class="select select-bordered w-full mt-2">
                    <option disabled selected>Choisir un étudiant</option>
                    <option>Jean Dupont</option>
                    <option>Marie Curie</option>
                </select>
            </div>
        </div>

        <!-- Validation Form -->
        <div class="col-span-2 card bg-base-100 shadow-xl">
            <div class="card-body">
                <h2 class="card-title">Validation AC</h2>

                <div class="overflow-x-auto">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>AC</th>
                                <th>Auto-positionnement (Étudiant)</th>
                                <th>Validation (Prof)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="ac in acs" :key="ac.code">
                                <td>
                                    <div class="font-bold">{{ ac.code }}</div>
                                    <div class="text-sm opacity-50">{{ ac.description }}</div>
                                </td>
                                <td>
                                    <div v-if="ac.studentDecl">
                                        <div class="badge badge-info">{{ ac.studentDecl.frequency }}</div>
                                        <div class="text-xs mt-1">{{ ac.studentDecl.comment }}</div>
                                    </div>
                                    <div v-else class="text-gray-400 italic">Non renseigné</div>
                                </td>
                                <td>
                                    <select v-model="ac.validationLevel" class="select select-sm select-bordered">
                                        <option :value="null">Non évalué</option>
                                        <option value="NOT_ACQUIRED">Non acquis</option>
                                        <option value="IN_PROGRESS">En cours</option>
                                        <option value="ACQUIRED">Acquis</option>
                                        <option value="MASTERED">Maîtrisé</option>
                                    </select>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="card-actions justify-end mt-4">
                    <button class="btn btn-primary">Valider l'entretien</button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const acs = ref([
    {
        code: 'AC11.01',
        description: 'Analyser l\'environnement',
        studentDecl: { frequency: 'OFTEN', comment: 'Utilisé pour l\'analyse PESTEL' },
        validationLevel: null
    },
    {
        code: 'AC11.02',
        description: 'Étude de marché',
        studentDecl: null,
        validationLevel: null
    }
])
</script>
