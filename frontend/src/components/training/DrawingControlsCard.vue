<template>
  <div class="drawing-controls q-pa-sm">
    <!-- Primary Drawing Controls -->
    <div class="text-subtitle1 q-mb-sm">{{ t('drawing.title') }}</div>
    <div class="row q-col-gutter-sm">
      <!-- Main drawing mode toggle with keyboard shortcuts -->
      <div class="col-12">
        <q-btn-toggle
          v-model="interactionMode"
          :options="[
            { label: t('drawing.modes.draw'), value: 'draw', icon: 'create' },
            { label: t('drawing.modes.pan'), value: 'pan', icon: 'pan_tool' },
            { label: t('drawing.modes.zoomIn'), value: 'zoom_in', icon: 'zoom_in' },
            { label: t('drawing.modes.zoomOut'), value: 'zoom_out', icon: 'zoom_out' }
          ]"
          @update:model-value="setInteractionMode"
          spread
          class="full-width"
          dense
        />
      </div>

      <!-- Drawing Configuration Section -->
      <div class="col-12">
        <q-expansion-item
          dense
          group="controls"
          icon="brush"
          :label="t('drawing.options.title')"
        >
          <q-card class="compact-card">
            <q-card-section class="q-pa-sm">
              <!-- Drawing Mode Toggle -->
              <div class="row items-center q-mb-sm">
                <div class="col">
                  <q-btn
                    :label="drawingMode === 'square' ? t('drawing.options.squareMode') : t('drawing.options.freehandMode')"
                    :icon="drawingMode === 'square' ? 'crop_square' : 'gesture'"
                    @click="toggleDrawingMode"
                    :color="drawingMode === 'square' ? 'primary' : 'secondary'"
                    class="full-width"
                    dense
                  />
                </div>
              </div>

              <!-- Polygon Size Slider -->
              <div class="text-caption q-mb-xs">{{ t('drawing.options.polygonSize') }}</div>
              <q-slider
                v-model="polygonSize"
                :min="10"
                :max="500"
                :step="10"
                label
                label-always
                color="primary"
                @update:model-value="updatePolygonSize"
                dense
              />
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </div>

      <!-- Class Selection Section -->
      <div class="col-12">
        <div class="text-subtitle2 q-mb-xs">{{ t('drawing.classes.title') }}</div>
        <div class="row q-col-gutter-xs">
          <div 
            v-for="(className, index) in projectClasses"
            :key="className"
            class="col-6"
          >
            <q-btn
              :label="`${className} (${index + 1})`"
              :color="selectedClass === className ? 'primary' : 'grey-4'"
              :text-color="selectedClass === className ? 'white' : 'black'"
              @click="setClassLabel(className)"
              class="full-width"
              dense
            />
          </div>
        </div>
      </div>

      <!-- Polygon Management Section -->
      <div class="col-12 q-mt-sm">
        <q-expansion-item
          dense
          group="controls"
          icon="settings"
          :label="t('drawing.management.title')"
        >
          <q-card>
            <q-card-section class="q-pa-md">
              <div class="row q-col-gutter-sm">
                <div class="col-6">
                  <q-btn class="full-width" :label="t('drawing.management.undo')" icon="undo" @click="undoLastDraw" :disable="interactionMode !== 'draw'" />
                </div>
                <div class="col-6">
                  <q-btn class="full-width" :label="t('drawing.management.save')" icon="save" @click="saveTrainingPolygons" />
                </div>
                <div class="col-6">
                  <q-btn class="full-width" :label="t('drawing.management.clear')" icon="delete_sweep" @click="clearDrawnPolygons" />
                </div>
                <div class="col-6">
                  <q-btn class="full-width" :label="t('drawing.management.delete')" icon="delete" @click="deleteSelectedFeature"/>
                </div>
                <div class="col-6">
                  <q-btn class="full-width" :label="t('drawing.management.download')" icon="download" @click="downloadPolygons" />
                </div>
                <div class="col-6">
                  <q-btn class="full-width" :label="t('drawing.management.load')" icon="upload_file" @click="triggerFileUpload" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </div>
    </div>

    <input type="file" ref="fileInput" style="display: none" accept=".geojson" @change="loadPolygons" />
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, watch, ref } from 'vue'
import { useMapStore } from 'src/stores/mapStore'
import { useProjectStore } from 'src/stores/projectStore'
import { useI18n } from 'vue-i18n'
import { useQuasar } from 'quasar'

export default {
    name: 'DrawingControlsCard',
    setup() {
        const mapStore = useMapStore()
        const projectStore = useProjectStore()
        const { t } = useI18n()
        const $q = useQuasar()
        const drawnPolygons = computed(() => mapStore.drawnPolygons)
        const selectedBasemapDate = computed(() => mapStore.selectedBasemapDate)

        const fileInput = ref(null)

        onMounted(async () => {
            window.addEventListener('keydown', handleKeyDown);

            if (projectClasses.value.length > 0 && !selectedClass.value) {
                selectedClass.value = projectClasses.value[0].name
            }
        })

        onUnmounted(() => {
            window.removeEventListener('keydown', handleKeyDown);
            mapStore.setInteractionMode('pan');
        })

        const polygonSize = computed({
            get: () => mapStore.polygonSize,
            set: (value) => mapStore.setPolygonSize(value)
        })

        const updatePolygonSize = (value) => {
            mapStore.setPolygonSize(value)
        }


        const interactionMode = computed({
            get: () => mapStore.interactionMode,
            set: (value) => mapStore.setInteractionMode(value)
        })

        const selectedClass = computed({
            get: () => mapStore.selectedClass,
            set: (value) => mapStore.setClassLabel(value)
        })

        const projectClasses = computed(() => {
            return projectStore.currentProject?.classes?.map(cls => cls.name) || []
        })

        const setInteractionMode = (mode) => {
            mapStore.setInteractionMode(mode)
        }

        const setClassLabel = (label) => {
            mapStore.setClassLabel(label)
        }

        const undoLastDraw = () => {
            mapStore.undoLastDraw()
        }

        const handleKeyDown = (event) => {

            if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
                return; // Ignore keyboard events when typing in input fields
            }

            const numKey = parseInt(event.key);

            if (numKey && numKey > 0 && numKey <= projectStore.projectClasses.length) {
                selectedClass.value = projectStore.projectClasses[numKey - 1]['name'];
                mapStore.setClassLabel(selectedClass.value);
                mapStore.setInteractionMode('draw');
            } else if ((event.key === 'Delete' || event.key === 'Backspace')) {
                mapStore.deleteSelectedFeature();
            } else if (event.key === 'm') {
                mapStore.setInteractionMode('pan');
            } else if ((event.ctrlKey || event.metaKey) && event.key === 'z') {
                event.preventDefault(); // Prevent the default undo behavior if necessary
                mapStore.undoLastDraw();
            } else if ((event.ctrlKey || event.metaKey) && event.key === 's') {
                event.preventDefault(); // Prevent the default undo behavior if necessary
                saveTrainingPolygons();
            } else if (event.key === 'z') {
                mapStore.setInteractionMode('zoom_in');
            } else if (event.key === 'x') {
                mapStore.setInteractionMode('zoom_out');
            } else if (event.key === 'd') {
                mapStore.setInteractionMode('draw');
            } else if (event.key == 'Escape') {
                mapStore.setInteractionMode('pan');
                mapStore.stopDrawing();
            } else if (event.key === 'f') {
                toggleDrawingMode();
            }
        };

        watch(drawnPolygons, () => {
            drawnPolygons.value = mapStore.drawnPolygons
        }, { immediate: true });

        watch(() => projectClasses.value, (newClasses) => {
            if (newClasses.length > 0 && !selectedClass.value) {
                selectedClass.value = newClasses[0]
            }
        }, { immediate: true })

        const saveTrainingPolygons = async () => {
            try {
                await mapStore.saveCurrentTrainingPolygons(selectedBasemapDate.value);
                // Show success notification
                $q.notify({
                    type: 'positive',
                    message: t('drawing.notifications.dateIncluded')
                });
            } catch (error) {
                // Show error notification
                $q.notify({
                    type: 'negative',
                    message: t('drawing.notifications.saveError')
                });
            }
        };

        const clearDrawnPolygons = () => {
            mapStore.clearDrawnPolygons(true)
        }

        const isCurrentDateExcluded = computed(() => {
            return projectStore.isDateExcluded(mapStore.selectedBasemapDate);
        });

        const toggleExcludeCurrentDate = async () => {
            try {
                await projectStore.toggleExcludedDate(mapStore.selectedBasemapDate);
                $q.notify({
                    type: 'positive',
                    message: isCurrentDateExcluded.value
                        ? t('drawing.notifications.dateIncluded')
                        : t('drawing.notifications.dateExcluded')
                });
            } catch (error) {
                $q.notify({
                    type: 'negative',
                    message: t('drawing.notifications.dateToggleError')
                });
            }
        };

        const deleteSelectedFeature = () => {
            if (mapStore.selectedFeature) {
                $q.dialog({
                    title: t('drawing.dialogs.delete.title'),
                    message: t('drawing.dialogs.delete.message'),
                    cancel: true,
                    persistent: true
                }).onOk(() => {
                    mapStore.deleteSelectedFeature();
                });
            } else {
                $q.notify({
                    type: 'negative',
                    message: t('drawing.notifications.noFeatureSelected')
                });
            }
        };

        const downloadPolygons = () => {
            const polygons = mapStore.drawnPolygons.map(polygon => ({
                ...polygon,
                properties: {
                    ...polygon.properties,
                    basemapDate: mapStore.selectedBasemapDate
                }
            }));
            const geojson = {
                type: "FeatureCollection",
                features: polygons
            };
            const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: "application/geo+json" });
            const url = URL.createObjectURL(blob);

            // Retrieve and sanitize the project name
            const projectNameRaw = projectStore.currentProject?.name || 'unknown_project';
            const projectName = projectNameRaw.replace(/[<>:"\/\\|?*\x00-\x1F]/g, '_').replace(/\s+/g, '_');

            const link = document.createElement('a');
            link.href = url;
            link.download = `training_polygons_${projectName}_${mapStore.selectedBasemapDate}.geojson`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        };

        const triggerFileUpload = () => {
            fileInput.value.click()
        };

        const loadPolygons = (event) => {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const geojson = JSON.parse(e.target.result);
                    if (geojson.type !== 'FeatureCollection') {
                        throw new Error('Invalid GeoJSON format');
                    }
                    geojson.features.forEach(feature => {
                        if (feature.geometry && feature.properties) {
                            mapStore.addPolygon({
                                ...feature,
                                properties: {
                                    ...feature.properties,
                                    basemapDate: feature.properties.basemapDate || mapStore.selectedBasemapDate
                                }
                            });
                        }
                    });
                    $q.notify({
                        type: 'positive',
                        message: t('drawing.notifications.polygonsLoaded')
                    });
                } catch (error) {
                    console.error('Error loading GeoJSON:', error);
                    $q.notify({
                        type: 'negative',
                        message: t('drawing.notifications.loadError')
                    });
                }
            };
            reader.readAsText(file);
            // Reset the file input
            event.target.value = null;
        };

        const drawingMode = computed(() => mapStore.drawingMode)

        const toggleDrawingMode = () => {
            mapStore.toggleDrawingMode()
        }

        return {
            interactionMode,
            selectedClass,
            projectClasses,
            setInteractionMode,
            setClassLabel,
            undoLastDraw,
            drawnPolygons,
            handleKeyDown,
            selectedBasemapDate,
            polygonSize,
            updatePolygonSize,
            saveTrainingPolygons,
            clearDrawnPolygons,
            isCurrentDateExcluded,
            toggleExcludeCurrentDate,
            deleteSelectedFeature,
            downloadPolygons,
            triggerFileUpload,
            loadPolygons,
            fileInput,
            drawingMode,
            toggleDrawingMode,
            t
        }
    }
}
</script>

<style scoped>
.drawing-controls {
  background-color: rgba(255, 255, 255, 1.0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.q-slider {
  width: 100%;
}

/* Add smooth transitions */
.q-btn {
  transition: all 0.3s ease;
}

/* Make expansion panels more compact */
:deep(.q-expansion-item__content) {
  padding: 0;
}

:deep(.q-card) {
  box-shadow: none;
}

/* Make the compact cards more compact */
.compact-card :deep(.q-card__section) {
  padding: 8px;
}

/* Ensure class selection buttons are compact but readable */
.text-subtitle2 {
  font-size: 0.9rem;
  margin-bottom: 4px;
}

/* Keep polygon management buttons larger */
.q-expansion-item[label="Polygon Management"] :deep(.q-btn) {
  padding: 8px 16px;
  min-height: 36px;
}
</style>
