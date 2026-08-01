import streamlit as st
import json

def create_default_config():
    return {
  "engine": {
	"modulus": 11
  },
  "domains": {
	"earth": { "display_name": "Earth" }
  },
  "operations": {
	"add":      { "max_modifier": 3, "time_per_point": 10 },
	"subtract": { "max_modifier": 3, "time_per_point": 10 },
	"multiply": { "max_modifier": 2, "time_per_point": 15 },
	"alter":    { "max_modifier": 2, "time_per_point": 20 }
  },
  "effects": {
	"pure": {
	  "low_healing": {
		"domain": "earth",
		"anchor": [7, 4, 3],
		"capture_radius": 5.0
	  },
	  "regeneration": {
		"domain": "earth",
		"anchor": [2, 6, 5],
		"capture_radius": 4.0
	  },
	  "instant_healing": {
		"domain": "earth",
		"anchor": [8, 8, 8],
		"capture_radius": 3.0
	  }
	},
	"combined": {
		
	}
  },
  "source_objects": {
	"basil": {
	  "tiers": {
		"standard": [
		  [2, 2, 2]
		]
	  }
	},
	"rosemary": {
	  "tiers": {
		"standard": [
		  [1, 3, 1]
		]
	  }
	},
	"sage": {
	  "tiers": {
		"standard": [
		  [1, 3, 3]
		]
	  }
	},
	"bay": {
	  "tiers": {
		"standard": [
		  [3, 4, 1]
		]
	  }
	}
  },
"alter_objects": {
  "potasium":     { "exponents": [4] },
  "phosphorus": { "exponents": [2] }
}
}


def init_state():
    if "config_data" not in st.session_state:
        st.session_state["config_data"] = None

def load_uploaded_config(uploaded_file):
    if uploaded_file is None:
        return
    content = uploaded_file.read().decode("utf-8")
    st.session_state["config_data"] = json.loads(content)

def render_loaded_config():
    st.success("Configuration loaded")
    st.json(st.session_state["config_data"])

    if st.button("Start over"):
        st.session_state["config_data"] = None
        st.rerun()

def render_editor():
    modulus = st.number_input(
        "Engine modulus",
        min_value=1,
        max_value=100,
        value=st.session_state["config_data"]["engine"]["modulus"]
    )

    st.session_state["config_data"]["engine"]["modulus"] = modulus

def main():
    st.title("Hello and welcome to the balance app")
    st.markdown("Please select an existing valid JSON configuration file or create one")

    init_state()

    if st.session_state["config_data"] is None:
        uploaded_file = st.file_uploader("Select a valid JSON configuration file", ".json")
        load_uploaded_config(uploaded_file)

        if st.button("Create JSON"):
            st.session_state["config_data"] = create_default_config()
            st.rerun()
    else:
        render_loaded_config()
        render_editor()

main()
