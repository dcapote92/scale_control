import pandas as pd
import streamlit as st
import plotly.express as px


SECTIONS = ['Para Revisão', 'Açougue', 'Frios', 'Peixaria', 'Hortifrúti', 'Padaria', 'Frente de Loja', 'Docas Secas', 'Doca Fria']
REFFERENCE_WEIGHT_35KG = 20000
REFFERENCE_WEIGHT_15KG = 10000

COLOR_MAP = {
    'OK': 'background-color: #4BBF73',
    'Tolerância': 'background-color: #FFC107',
    'Calibração': 'background-color: #DC3545',
    'default': ''
}


def highlight_status_row(row):
    color_name = row['Status_Cor']
    style = COLOR_MAP.get(color_name, COLOR_MAP['default'])
    return [style] * len(row)


def main():
    st.set_page_config(layout="wide")

    file = st.file_uploader('Abrir Arquivo CSV', type=['csv'])

    if file:
        try:
            data = pd.read_csv(file, index_col=False)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {e}")
            return
    else:
        st.info("Por favor, faça o upload do arquivo de balanças CSV.")
        return

    st.title('Controle de Balanças')

    if data is not None:
        data.columns = data.columns.str.strip()

        if 'Balança' in data.columns:
            data['Balança'] = data['Balança'].fillna(0).astype(int).astype(str)

        difference_35kg = abs(data['Peso'] - REFFERENCE_WEIGHT_35KG)
        difference_15kg = abs(data['Peso'] - REFFERENCE_WEIGHT_15KG)

        mask_ok = (data['Peso'] == REFFERENCE_WEIGHT_35KG) | (data['Peso'] == REFFERENCE_WEIGHT_15KG)

        mask_35kg_tolerance = (difference_35kg >= 1) & (difference_35kg <= 5)
        mask_15kg_tolerance = (difference_15kg >= 1) & (difference_15kg <= 5)

        mask_tolerance = (
            (data['Peso Máximo'] == 35000) & mask_35kg_tolerance
        ) | (
            (data['Peso Máximo'] == 15000) & mask_15kg_tolerance
        )

        mask_35kg_calibration = difference_35kg > 5
        mask_15kg_calibration = difference_15kg > 5

        mask_calibration = (
            (data['Peso Máximo'] == 35000) & mask_35kg_calibration
        ) | (
            (data['Peso Máximo'] == 15000) & mask_15kg_calibration
        )

        data['Status_Cor'] = 'default'
        data.loc[mask_calibration, 'Status_Cor'] = 'Calibração'
        data.loc[mask_tolerance, 'Status_Cor'] = 'Tolerância'
        data.loc[mask_ok, 'Status_Cor'] = 'OK'

        mask_to_review = data['Status_Cor'].isin(['Tolerância', 'Calibração'])
        data_to_review = data[mask_to_review].copy()

        count_ok = len(data[mask_ok])
        count_tolerance = len(data[mask_tolerance])
        count_calibration = len(data[mask_calibration])

        col_metrics, col_chart = st.columns([4, 6])

        with col_metrics:
            col_total_scales, col_Peso, col_on_tolerance, col_need_calibration = st.columns(4)

            col_total_scales.metric('Total', data.shape[0], border=True)
            col_Peso.metric('OK', count_ok, border=True)
            col_on_tolerance.metric('± 5g', count_tolerance, border=True)
            col_need_calibration.metric('> 5g', count_calibration, border=True)

        with col_chart:
            df_chart = pd.DataFrame({
                'Status': ['OK', 'Tolerância', 'Calibração'],
                'Contagem': [count_ok, count_tolerance, count_calibration]
            })

            color_discrete_map = {
                'OK': '#4BBF73',
                'Tolerância': '#FFC107',
                'Calibração': '#DC3545'
            }

            fig = px.pie(
                df_chart,
                values='Contagem',
                names='Status',
                title='Distribuição do Status das Balanças',
                color='Status',
                color_discrete_map=color_discrete_map
            )

            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=True)
            fig.update_traces(textposition='inside', textinfo='percent+value')

            st.plotly_chart(fig, width='stretch')

        existing_sections = data['Setor'].unique()

        tabs = st.tabs(SECTIONS)

        for i, section in enumerate(SECTIONS):
            if section == 'Para Revisão':
                df_section = data_to_review
                if not df_section.empty:
                    with tabs[i]:
                        st.subheader(section)
                        format_dict = {
                            'Peso': lambda x: '{:,.0f}'.format(x).replace(',', '.'),
                            'Peso Máximo': lambda x: '{:,.0f}'.format(x).replace(',', '.')
                        }

                        df_estilizado = df_section.style.apply(
                            highlight_status_row, axis=1).format(format_dict).hide(axis=1, subset=['Status_Cor'])

                        st.dataframe(df_estilizado, width='stretch')
                else:
                    with tabs[i]:
                        st.info('🎉 Nenhuma balança precisa de **Revisão/Calibração** no momento. Todas OK!')

            elif section in existing_sections:
                with tabs[i]:
                    st.subheader(section)
                    df_section = data[data['Setor'] == section]

                    format_dict = {
                        'Peso': lambda x: '{:,.0f}'.format(x).replace(',', '.'),
                        'Peso Máximo': lambda x: '{:,.0f}'.format(x).replace(',', '.')
                    }

                    df_estilizado = df_section.style.apply(
                        highlight_status_row, axis=1).format(format_dict).hide(axis=1, subset=['Status_Cor'])

                    st.dataframe(df_estilizado, width='stretch')
            else:
                with tabs[i]:
                    st.info(f'Nenhuma balança encontrada para o setor: **{section}**')


if __name__ == '__main__':
    main()
