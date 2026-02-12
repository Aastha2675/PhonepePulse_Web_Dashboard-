document.addEventListener("DOMContentLoaded", initMap);


let map;
let geoLayer;
let activeLayer = null;

function initMap() {
  map = L.map("india-map", {
    zoomControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false
  });

  loadIndiaGeoJSON();
}

async function loadIndiaGeoJSON() {
  try {
    const res = await fetch("/assets/states_india.geojson"); 
    const data = await res.json();

    geoLayer = L.geoJSON(data, {
      style: defaultStyle,
      onEachFeature: onEachState
    }).addTo(map);

    map.fitBounds(geoLayer.getBounds());

  } catch (err) {
    console.error("GeoJSON load failed:", err);
  }
}

function defaultStyle() {
  return {
    fillColor: "#5b2d8b",
    weight: 1,
    color: "#ffffff",
    fillOpacity: 0.6
  };
}

// SINGLE onEachState ONLY
function onEachState(feature, layer) {
  layer.on({
    click: () => {
      const stateName = feature.properties.st_nm; 
      onStateClick(stateName);
    },
    mouseover: e => {
      e.target.setStyle({ fillOpacity: 0.85 });
    },
    mouseout: e => {
      geoLayer.resetStyle(e.target);
    }
  });
}


function onStateClick(stateName) {
  select_state = stateName;

  document.getElementById("title").innerText =
    (select_category === "insurance" ? "Insurance - " : "Transaction - ") +
    stateName;

  // highlight selected state
  if (activeLayer) {
    geoLayer.resetStyle(activeLayer);
  }

  geoLayer.eachLayer(layer => {
    if (layer.feature.properties.st_nm === stateName) {
      layer.setStyle({
        fillColor: "#3b0a6f",
        fillOpacity: 0.9
      });
      activeLayer = layer;
    }
  });

  triggerDataFetch(select_state);
}



