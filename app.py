import streamlit as st
import pandas as pd
import pickle
import os
from backend import Bracket

# --- NOME DO ARQUIVO DE CACHE ---
STATE_FILE = "championship_state.pkl"

# --- FUNÇÕES PARA SALVAR E CARREGAR O ESTADO ---

def save_state(state):
    """Salva o objeto do campeonato em um arquivo pickle."""
    with open(STATE_FILE, "wb") as f:
        pickle.dump(state, f)

def load_state():
    """Carrega o objeto do campeonato de um arquivo pickle, se existir."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "rb") as f:
            try:
                return pickle.load(f)
            except EOFError: # Lida com o caso de arquivo vazio ou corrompido
                return None
    return None

# --- TEMA E ÍCONE DA PÁGINA ---
st.set_page_config(
    page_title="Revo Challenge",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# A função display_match_results não precisa de alteração.
def display_match_results(bracket_side, bracket_data):
    st.subheader(f"Jogos da Chave {bracket_side.capitalize()}")
    with st.form(key=f"form_{bracket_side}"):
        for i, match in enumerate(bracket_data, 1):
            dupla1_str = f"{match['first'][0]} & {match['first'][1]}"
            dupla2_str = f"{match['second'][0]} & {match['second'][1]}"
            with st.container(border=True):
                st.markdown(f"**Jogo {i}**: `{dupla1_str}` vs `{dupla2_str}`")
                if match.get('winner'):
                    score1, score2 = match.get('score1', 'N/A'), match.get('score2', 'N/A')
                    if match['winner'] == 'dupla1': st.success(f"👑 Vencedor: {dupla1_str}")
                    elif match['winner'] == 'dupla2': st.success(f"👑 Vencedor: {dupla2_str}")
                    elif match['winner'] == 'draw': st.info("🤝 Empate")
                    st.write(f"Placar Final: **{score1}** a **{score2}**")
                else:
                    cols = st.columns([2, 2])
                    with cols[0]: score1 = st.number_input(f"Placar: {dupla1_str}", min_value=0, key=f"{bracket_side}_{i}_score1")
                    with cols[1]: score2 = st.number_input(f"Placar: {dupla2_str}", min_value=0, key=f"{bracket_side}_{i}_score2")
        submitted = st.form_submit_button("Registrar Pontuações da Chave", use_container_width=True)
        if submitted:
            for i, match in enumerate(bracket_data, 1):
                if not match.get('winner'):
                    score1_val = st.session_state[f"{bracket_side}_{i}_score1"]
                    score2_val = st.session_state[f"{bracket_side}_{i}_score2"]
                    if score1_val > score2_val: match['winner'] = 'dupla1'
                    elif score2_val > score1_val: match['winner'] = 'dupla2'
                    else: match['winner'] = 'draw'
                    match['score1'], match['score2'] = score1_val, score2_val
            save_state(st.session_state.bracket_maker) # SALVA O ESTADO
            st.toast(f"Resultados da Chave {bracket_side.capitalize()} salvos!")
            st.rerun()

# A função de ranking não precisa de alterações.
def calculate_and_display_ranking(bracket_side_name, bracket_data, athletes_list):
    st.subheader(f"Ranking da Chave {bracket_side_name.capitalize()}")
    point_counts = {player: 0 for player in athletes_list}
    for match in bracket_data:
        if 'winner' in match:
            pair1_players, pair2_players = match['first'], match['second']
            score1, score2 = match.get('score1', 0), match.get('score2', 0)
            for player in pair1_players:
                if player in point_counts: point_counts[player] += score1
            for player in pair2_players:
                if player in point_counts: point_counts[player] += score2
    if not any(point_counts.values()):
        st.info("Aguardando o registro dos primeiros resultados.")
        return
    ranking_df = pd.DataFrame(list(point_counts.items()), columns=['Atleta', 'Pontos'])
    ranking_df = ranking_df.sort_values(by='Pontos', ascending=False).reset_index(drop=True)
    ranking_df.index += 1
    ranking_df = ranking_df.rename_axis('Posição').reset_index()
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)


def main():
    st.title("Painel do Campeonato")

    # --- LÓGICA DE CARREGAMENTO DO ESTADO ---
    # Se o 'bracket_maker' não está na sessão, tenta carregar do arquivo
    if 'bracket_maker' not in st.session_state:
        loaded_bracket_maker = load_state()
        if loaded_bracket_maker:
            st.session_state.bracket_maker = loaded_bracket_maker
            st.toast("Progresso anterior restaurado!")
        else:
            st.session_state.bracket_maker = Bracket(limit=8)

    bracket_maker = st.session_state.bracket_maker

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.header("⚙️ Configuração")
        
        with st.expander("Adicionar Atletas", expanded=not bracket_maker.athlete_by_side['left'].values):
            is_random_assignment = st.toggle("Distribuir aleatoriamente", value=True, help="Distribuição aleatória ou manual.")
            if is_random_assignment:
                athletes_input = st.text_area("Insira todos os nomes (um por linha)", height=250)
                if st.button("Adicionar e Sortear Lados"):
                    athletes = [name.strip() for name in athletes_input.split('\n') if name.strip()]
                    if athletes and len(athletes) % 2 == 0:
                        st.session_state.bracket_maker = Bracket(limit=len(athletes) // 2)
                        for athlete in athletes: st.session_state.bracket_maker.add_athlete(athlete, random=True)
                        save_state(st.session_state.bracket_maker) # SALVA O ESTADO
                        st.rerun()
                    else: st.error("Insira um número par de atletas.")
            else:
                left_athletes_input = st.text_area("Atletas do Lado Esquerdo", height=150)
                right_athletes_input = st.text_area("Atletas do Lado Direito", height=150)
                if st.button("Adicionar Atletas Manualmente"):
                    left_athletes = [name.strip() for name in left_athletes_input.split('\n') if name.strip()]
                    right_athletes = [name.strip() for name in right_athletes_input.split('\n') if name.strip()]
                    if left_athletes and len(left_athletes) == len(right_athletes):
                        st.session_state.bracket_maker = Bracket(limit=len(left_athletes))
                        for athlete in left_athletes: st.session_state.bracket_maker.add_athlete(athlete, side='left')
                        for athlete in right_athletes: st.session_state.bracket_maker.add_athlete(athlete, side='right')
                        save_state(st.session_state.bracket_maker) # SALVA O ESTADO
                        st.rerun()
                    else: st.error("Ambos os lados devem ter o mesmo número de atletas.")

        st.markdown("---")
        # Botão para resetar o campeonato
        st.warning("Atenção: A ação abaixo é irreversível.")
        if st.button("🔴 Resetar Campeonato", use_container_width=True):
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
            st.session_state.clear()
            st.rerun()

    # (O resto da lógica de exibição permanece a mesma)
    st.markdown("---")
    st.header("Atletas por Chave")
    col1, col2 = st.columns(2)
    left_athletes_list = list(bracket_maker.athlete_by_side['left'].values)
    right_athletes_list = list(bracket_maker.athlete_by_side['right'].values)
    with col1:
        st.subheader(f"Lado Esquerdo ({len(left_athletes_list)} atletas)")
        if left_athletes_list: st.info(", ".join(left_athletes_list))
        else: st.warning("Nenhum atleta adicionado.")
    with col2:
        st.subheader(f"Lado Direito ({len(right_athletes_list)} atletas)")
        if right_athletes_list: st.info(", ".join(right_athletes_list))
        else: st.warning("Nenhum atleta adicionado.")
            
    st.markdown("---")

    if left_athletes_list and right_athletes_list and not bracket_maker.brackets['left']:
        if st.button("Gerar Jogos", use_container_width=True, type="primary"):
            bracket_maker.gen_combinations('left'); bracket_maker.gen_combinations('right')
            bracket_maker.gen_brackets()
            save_state(bracket_maker) # SALVA O ESTADO
            st.rerun()

    left_display_brackets = bracket_maker.shuffle_brackets['left'] or bracket_maker.brackets['left']
    right_display_brackets = bracket_maker.shuffle_brackets['right'] or bracket_maker.brackets['right']

    if left_display_brackets:
        st.header("Resultados dos Jogos")
        if st.button("Embaralhar Ordem dos Jogos", use_container_width=True):
            bracket_maker.gen_shuffle_brackets('left'); bracket_maker.gen_shuffle_brackets('right')
            save_state(bracket_maker) # SALVA O ESTADO
            st.rerun()
        col3, col4 = st.columns(2)
        with col3: display_match_results('esquerda', left_display_brackets)
        with col4: display_match_results('direita', right_display_brackets)
        st.markdown("---")
        st.header("🏆 Ranking de Pontos")
        has_results = any('winner' in match for match in left_display_brackets) or any('winner' in match for match in right_display_brackets)
        if has_results:
            rank_col1, rank_col2 = st.columns(2)
            with rank_col1: calculate_and_display_ranking("Esquerda", left_display_brackets, left_athletes_list)
            with rank_col2: calculate_and_display_ranking("Direita", right_display_brackets, right_athletes_list)
        else: st.info("O ranking será exibido aqui assim que os primeiros resultados forem registrados.")

if __name__ == "__main__":
    main()