import streamlit as st
import ollama
import json
import re

st.set_page_config(
    page_title="AI Meal Planner",
    page_icon="🍽️",
    layout="centered"
)

st.title("🍽️ AI Meal Planner")
st.write("Find recipes based on your taste using Llama 3.2:3B")

# -------------------------------
# Generate Recipe List
# -------------------------------
def get_recipe_list(category, preference):

    prompt = f"""
You are a recipe recommendation assistant.

The user wants {category} recipes.
Their preference is: {preference}

Give exactly 5 recipe names.

Return ONLY valid JSON in this format:
{{
    "recipes": [
        "Recipe 1",
        "Recipe 2",
        "Recipe 3",
        "Recipe 4",
        "Recipe 5"
    ]
}}
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response["message"]["content"]

    try:
        data = json.loads(text)
        return data["recipes"]
    except:
        # Backup method if model adds extra text
        match = re.search(r'\[.*\]', text, re.DOTALL)

        if match:
            return json.loads(match.group())["recipes"]

        return []


# -------------------------------
# Generate Selected Recipe
# -------------------------------
def get_recipe_details(recipe):

    prompt = f"""
You are a recipe assistant.

Give information about this recipe:

Recipe: {recipe}

Return ONLY valid JSON using this exact structure:

{{
    "ingredients": [
        "ingredient 1",
        "ingredient 2",
        "ingredient 3"
    ],
    "process": [
        "Step 1",
        "Step 2",
        "Step 3"
    ],
    "cooking_time": "30 minutes",
    "servings": "2 people",
    "nutrition": {{
        "calories": "450 kcal",
        "protein": "12 g",
        "carbohydrates": "60 g",
        "fat": "18 g"
    }}
}}

The nutrition values are SAMPLE ESTIMATES for demonstration only.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response["message"]["content"]

    try:
        return json.loads(text)
    except:
        # Remove markdown code fences if present
        text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text)
        except:
            return None


# -------------------------------
# User Input
# -------------------------------

st.subheader("👤 Tell us your preference")

category = st.selectbox(
    "What type of recipe do you want?",
    ["Sweet 🍰", "Hot / Spicy 🌶️"]
)

preference = st.text_input(
    "What do you like?",
    placeholder="Example: Chocolate, Chicken, Paneer..."
)


# -------------------------------
# Recipe Search
# -------------------------------

if st.button("🔍 Find Recipes"):

    if preference.strip() == "":
        st.warning("Please enter your food preference.")
    else:

        with st.spinner("🤖 Llama is finding recipes..."):

            recipes = get_recipe_list(
                category,
                preference
            )

        if recipes:

            st.session_state["recipes"] = recipes

            st.success("Here are some recipes for you! 🍽️")

            for i, recipe in enumerate(recipes, 1):
                st.write(f"### {i}. {recipe}")

        else:
            st.error("Unable to generate recipes. Please try again.")


# -------------------------------
# Recipe Selection
# -------------------------------

if "recipes" in st.session_state:

    st.divider()

    st.subheader("🍴 Select a Recipe")

    selected_recipe = st.selectbox(
        "Choose one recipe:",
        st.session_state["recipes"]
    )

    if st.button("📖 Get Recipe Details"):

        with st.spinner("👩‍🍳 Preparing recipe details..."):

            details = get_recipe_details(
                selected_recipe
            )

        if details:

            st.success(
                f"Recipe details for {selected_recipe}"
            )

            # Ingredients
            st.subheader("🥘 Ingredients")

            for ingredient in details["ingredients"]:
                st.write("•", ingredient)

            # Process
            st.subheader("👩‍🍳 Preparation Process")

            for i, step in enumerate(
                details["process"], 1
            ):
                st.write(f"**Step {i}:** {step}")

            # Time & Servings
            st.subheader("⏱️ Recipe Information")

            col1, col2 = st.columns(2)

            with col1:
                st.info(
                    f"⏱️ Cooking Time\n\n"
                    f"{details['cooking_time']}"
                )

            with col2:
                st.info(
                    f"🍽️ Servings\n\n"
                    f"{details['servings']}"
                )

            # Nutrition
            st.subheader("📊 Sample Nutrition")

            nutrition = details["nutrition"]

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "🔥 Calories",
                    nutrition["calories"]
                )

                st.metric(
                    "💪 Protein",
                    nutrition["protein"]
                )

            with col2:
                st.metric(
                    "🍞 Carbohydrates",
                    nutrition["carbohydrates"]
                )

                st.metric(
                    "🥑 Fat",
                    nutrition["fat"]
                )

            st.caption(
                "⚠️ Nutrition values shown are sample estimates "
                "generated for demonstration purposes."
            )

        else:
            st.error(
                "Could not generate recipe details."
            )