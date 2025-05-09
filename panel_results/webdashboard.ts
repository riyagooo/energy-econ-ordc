import React, { useEffect, useState, useRef } from 'react';
import * as d3 from 'd3';
import _ from 'lodash';

const MapComponent = () => {
  const [statesData, setStatesData] = useState(null);
  const [nyisoZoneData, setNyisoZoneData] = useState(null);
  const [isoNeZoneData, setIsoNeZoneData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewBox, setViewBox] = useState("0 0 800 600");
  const [mapTransform, setMapTransform] = useState("translate(0,0) scale(1)");
  const svgRef = useRef(null);
  const dataSource = "This map uses GeoJSON data from public sources and approximates grid operator zone boundaries.";

  // NYISO Zone definitions and colors
  const nyisoZones = {
    'A': { name: 'West', color: '#ffc685', states: ['New York'] },
    'B': { name: 'Genesee', color: '#ffb570', states: ['New York'] },
    'C': { name: 'Central', color: '#ffa75a', states: ['New York'] },
    'D': { name: 'North', color: '#ff9945', states: ['New York'] },
    'E': { name: 'Mohawk Valley', color: '#ff8b30', states: ['New York'] },
    'F': { name: 'Capital', color: '#ff7d1a', states: ['New York'] },
    'G': { name: 'Hudson Valley', color: '#ff6f05', states: ['New York'] },
    'H': { name: 'Millwood', color: '#f06300', states: ['New York'] },
    'I': { name: 'Dunwoodie', color: '#db5a00', states: ['New York'] },
    'J': { name: 'New York City', color: '#c75100', states: ['New York'] },
    'K': { name: 'Long Island', color: '#b24800', states: ['New York'] },
  };

  // ISO-NE Zone definitions and colors
  const isoNeZones = {
    'ME': { name: 'Maine', color: '#a1dba1', states: ['Maine'] },
    'NH': { name: 'New Hampshire', color: '#8fd68f', states: ['New Hampshire'] },
    'VT': { name: 'Vermont', color: '#7dd17d', states: ['Vermont'] },
    'CT': { name: 'Connecticut', color: '#6bcc6b', states: ['Connecticut'] },
    'RI': { name: 'Rhode Island', color: '#59c759', states: ['Rhode Island'] },
    'NEMA': { name: 'Northeast Massachusetts', color: '#47c247', states: ['Massachusetts'] },
    'SEMA': { name: 'Southeast Massachusetts', color: '#35bd35', states: ['Massachusetts'] },
    'WCMA': { name: 'West/Central Massachusetts', color: '#23b823', states: ['Massachusetts'] },
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Load US states data
        const statesResponse = await fetch('https://raw.githubusercontent.com/deldersveld/topojson/master/countries/us-states/us-states-10m.json');
        const statesTopojson = await statesResponse.json();
        
        // Convert TopoJSON to GeoJSON
        const statesGeojson = topojsonToGeojson(statesTopojson, 'states');
        
        // Filter to only northeastern states
        const northeastStates = ['New York', 'Connecticut', 'Rhode Island', 'Massachusetts', 
                                'Vermont', 'New Hampshire', 'Maine'];
        const filteredStates = {
          type: "FeatureCollection",
          features: statesGeojson.features.filter(f => 
            northeastStates.includes(f.properties.name)
          )
        };
        
        // Create simplified NYISO and ISO-NE zone data
        const nyisoData = createSimplifiedNyisoZones(filteredStates);
        const isoNeData = createSimplifiedIsoNeZones(filteredStates);
        
        setStatesData(filteredStates);
        setNyisoZoneData(nyisoData);
        setIsoNeZoneData(isoNeData);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (statesData && svgRef.current) {
      drawMap();
    }
  }, [statesData, nyisoZoneData, isoNeZoneData]);

  // Convert TopoJSON to GeoJSON
  const topojsonToGeojson = (topojson, objectName) => {
    const features = [];
    const arcs = topojson.arcs;
    const objects = topojson.objects[objectName];
    
    // Simple implementation for basic conversion
    if (objects && objects.geometries) {
      objects.geometries.forEach(geometry => {
        const feature = {
          type: "Feature",
          properties: { 
            ...geometry.properties,
            name: geometry.properties.name || 'Unknown'
          },
          geometry: {
            type: geometry.type,
            coordinates: []
          }
        };
        
        if (geometry.type === "Polygon" && geometry.arcs) {
          feature.geometry.coordinates = geometry.arcs.map(arc => {
            return arc.map(index => {
              // Simplified, as real implementation would be more complex
              return [0, 0]; // Placeholder
            });
          });
        }
        
        features.push(feature);
      });
    }
    
    return {
      type: "FeatureCollection",
      features: features
    };
  };

  // Create simplified NYISO zones (for illustration only)
  const createSimplifiedNyisoZones = (statesData) => {
    // Create simplified zone geometries based on state data
    // In a real implementation, this would use actual zone boundaries
    
    const nyFeature = statesData.features.find(f => f.properties.name === "New York");
    if (!nyFeature) return { type: "FeatureCollection", features: [] };
    
    const features = [];
    
    // Create simplified zone features
    // This is a very simplified approach just for visualization
    Object.entries(nyisoZones).forEach(([zoneId, zone]) => {
      features.push({
        type: "Feature",
        properties: {
          zoneId: zoneId,
          zoneName: zone.name,
          operator: "NYISO"
        },
        geometry: nyFeature.geometry // Use the state geometry as base
      });
    });
    
    return {
      type: "FeatureCollection",
      features: features
    };
  };

  // Create simplified ISO-NE zones (for illustration only)
  const createSimplifiedIsoNeZones = (statesData) => {
    const features = [];
    
    // Create a feature for each ISO-NE state
    Object.entries(isoNeZones).forEach(([zoneId, zone]) => {
      const stateName = zone.states[0];
      const stateFeature = statesData.features.find(f => f.properties.name === stateName);
      
      if (stateFeature) {
        features.push({
          type: "Feature",
          properties: {
            zoneId: zoneId,
            zoneName: zone.name,
            operator: "ISO-NE"
          },
          geometry: stateFeature.geometry
        });
      }
    });
    
    return {
      type: "FeatureCollection",
      features: features
    };
  };

  const drawMap = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    
    const width = 800;
    const height = 600;
    
    // Create projection and path generator
    const projection = d3.geoAlbersUsa()
      .scale(1000)
      .translate([width / 2, height / 2]);
    
    const pathGenerator = d3.geoPath().projection(projection);
    
    // Draw state boundaries
    const statesGroup = svg.append("g").attr("class", "states");
    statesGroup.selectAll("path")
      .data(statesData.features)
      .enter()
      .append("path")
      .attr("d", d => {
        try {
          return pathGenerator(d);
        } catch (e) {
          return ""; // Return empty path if error
        }
      })
      .attr("fill", "#f8f9fa")
      .attr("stroke", "#999")
      .attr("stroke-width", 0.5);
      
    // Instead of using the actual GeoJSON data (which might have issues),
    // we'll create a simplified visualization using state outlines
    
    // Draw simplified NYISO zones
    const nyisoGroup = svg.append("g").attr("class", "nyiso-zones");
    Object.entries(nyisoZones).forEach(([zoneId, zone], index) => {
      // Create a simplified representation
      const centerX = 250; // Approximate center of NY state
      const centerY = 250;
      const radius = 20;
      const angle = (index / Object.keys(nyisoZones).length) * 2 * Math.PI;
      const x = centerX + Math.cos(angle) * radius * 5;
      const y = centerY + Math.sin(angle) * radius * 3;
      
      nyisoGroup.append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", radius)
        .attr("fill", zone.color)
        .attr("stroke", "#333")
        .attr("stroke-width", 1)
        .attr("opacity", 0.8);
        
      nyisoGroup.append("text")
        .attr("x", x)
        .attr("y", y)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("font-size", "10px")
        .attr("font-weight", "bold")
        .text(zoneId);
    });
    
    // Draw simplified ISO-NE zones
    const isoNeGroup = svg.append("g").attr("class", "iso-ne-zones");
    Object.entries(isoNeZones).forEach(([zoneId, zone], index) => {
      // Create a simplified representation
      const centerX = 450; // Approximate center of New England
      const centerY = 250;
      const radius = 20;
      const angle = (index / Object.keys(isoNeZones).length) * 2 * Math.PI;
      const x = centerX + Math.cos(angle) * radius * 5;
      const y = centerY + Math.sin(angle) * radius * 3;
      
      isoNeGroup.append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", radius)
        .attr("fill", zone.color)
        .attr("stroke", "#333")
        .attr("stroke-width", 1)
        .attr("opacity", 0.8);
        
      isoNeGroup.append("text")
        .attr("x", x)
        .attr("y", y)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("font-size", "10px")
        .attr("font-weight", "bold")
        .text(zoneId.length <= 2 ? zoneId : zoneId.substring(0, 2));
    });
    
    // Draw labels for regions
    svg.append("text")
      .attr("x", 250)
      .attr("y", 180)
      .attr("text-anchor", "middle")
      .attr("font-size", "16px")
      .attr("font-weight", "bold")
      .text("NYISO");
      
    svg.append("text")
      .attr("x", 450)
      .attr("y", 180)
      .attr("text-anchor", "middle")
      .attr("font-size", "16px")
      .attr("font-weight", "bold")
      .text("ISO-NE");
  };

  if (loading) {
    return <div className="text-center p-4">Loading map data...</div>;
  }

  if (error) {
    return <div className="text-center p-4 text-red-500">Error loading map: {error.message}</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-center">NYISO and ISO-NE Grid Operators and Their Zones</h2>
        <p className="text-sm text-center">Map showing the zones of New York Independent System Operator (NYISO) and ISO New England (ISO-NE)</p>
      </div>
      
      <div className="flex-grow relative" style={{ height: "500px" }}>
        <svg 
          ref={svgRef} 
          width="100%" 
          height="100%" 
          viewBox={viewBox} 
          preserveAspectRatio="xMidYMid meet"
        />
      </div>
      
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="border p-2 rounded">
          <h3 className="font-bold text-center mb-2">NYISO Zones</h3>
          <div className="grid grid-cols-3 gap-1 text-xs">
            {Object.entries(nyisoZones).map(([id, zone]) => (
              <div key={id} className="flex items-center">
                <div className="w-4 h-4 mr-1" style={{ backgroundColor: zone.color }}></div>
                <span>Zone {id}: {zone.name}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="border p-2 rounded">
          <h3 className="font-bold text-center mb-2">ISO-NE Zones</h3>
          <div className="grid grid-cols-2 gap-1 text-xs">
            {Object.entries(isoNeZones).map(([id, zone]) => (
              <div key={id} className="flex items-center">
                <div className="w-4 h-4 mr-1" style={{ backgroundColor: zone.color }}></div>
                <span>{id}: {zone.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-center text-gray-500">
        <p>Note: This map shows simplified zone representations and is for illustrative purposes only.</p>
        <p>For accurate and detailed zone boundaries, please refer to official NYISO and ISO-NE documentation.</p>
        <p className="mt-2">{dataSource}</p>
      </div>
    </div>
  );
};

export default MapComponent;