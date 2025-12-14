import streamlit as st
import pandas as pd


SECTIONS = ['Açougue', 'Frios', 'Peixaria', 'Hortifrúti', 'Padaria', 'Frente de Loja', 'Docas Secas', 'Doca Fria']
REFFERENCE_WEIGHT_35KG = 20000
REFFERENCE_WEIGHT_15KG = 10000

COLOR_MAP = {
    'OK': 'background-color: #08c73b',
    'Tolerância': 'background-color: #a89505',
    'Calibração': 'background-color: #a80518',
    'default': ''
}


def highlight_status_row(row):
    color_name = row['Status_Cor']
    style = COLOR_MAP.get(color_name, COLOR_MAP['default'])

    return [style] * len(row)


def main():
    try:
        file = 'rel_sm541_export.csv'
        data = pd.read_csv(file)
    except FileNotFoundError:
        st.error(f'Erro: O arquivo {file} não foi encontrado')
        return

    st.title('Controle de Balanças')
    col_total_scales, col_Peso, col_on_tolerance, col_need_calibration = st.columns(4)

    difference_35kg = abs(data['Peso'] - REFFERENCE_WEIGHT_35KG)
    difference_15kg = abs(data['Peso'] - REFFERENCE_WEIGHT_15KG)

    mask_ok = (data['Peso'] == REFFERENCE_WEIGHT_35KG) | (data['Peso'] == REFFERENCE_WEIGHT_15KG)
    mask_35kg_tolerance = (difference_35kg >= 1) & (difference_35kg <= 5)
    mask_15kg_tolerance = (difference_15kg >= 1) & (difference_15kg <= 5)

    mask_35kg_calibration = difference_35kg > 5
    mask_15kg_calibration = difference_15kg > 5

    mask_tolerance = (
        (data['Peso Máximo'] == 35000) & mask_35kg_tolerance
    ) | (
        (data['Peso Máximo'] == 15000) & mask_15kg_tolerance
    )

    mask_calibration = (
        (data['Peso Máximo'] == 35000) & mask_35kg_calibration
    ) | (
        (data['Peso Máximo'] == 15000) & mask_15kg_calibration
    )

    data['Status_Cor'] = 'default'

    data.loc[mask_calibration, 'Status_Cor'] = 'Calibração'
    data.loc[mask_tolerance, 'Status_Cor'] = 'Tolerância'
    data.loc[mask_ok, 'Status_Cor'] = 'OK'

    count_ok = len(data[mask_ok])
    count_tolerance = len(data[mask_tolerance])
    count_calibration = len(data[mask_calibration])

    col_total_scales.metric(
        'Total de Balanças',
        data.shape[0],
        border=True,
    )

    col_Peso.metric(
        'Peso OK',
        count_ok,
        border=True,
        delta=count_ok,
        delta_color='normal'
    )

    col_on_tolerance.metric(
        'Tolerância: ± 5g',
        count_tolerance,
        border=True,
        delta=count_tolerance,
        delta_color='off'
    )

    col_need_calibration.metric(
        'Calibração: > 5g',
        count_calibration,
        border=True,
        delta=count_calibration,
        delta_color='inverse'
    )

    existing_sections = data['Setor'].unique()
    tabs = st.tabs(SECTIONS)

    for i, section in enumerate(SECTIONS):
        if section in existing_sections:
            with tabs[i]:
                st.subheader(section)

                df_section = data[data['Setor'] == section]
                df_estilized = df_section.style.apply(highlight_status_row, axis=1).hide(axis=1, subset=['Status_Cor'])

                st.dataframe(
                    df_estilized,
                    width='stretch'
                )
        else:
            with tabs[i]:
                st.info(f'Nenhuma balança encontrada para o setor: **{section}**')


if __name__ == '__main__':
    main()
