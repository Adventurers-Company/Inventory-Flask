"""
Serviço de Cálculo de Bônus
Calcula stats do set equipado com fórmulas MMORPG
"""
from app.models.equipment_slot import EquipSlot

class CalculationService:
    """Calcula bônus e stats do jogador com 13 atributos base"""
    
    @staticmethod
    def calculate_player_stats(player):
        """
        Calcula todos os stats baseados no set equipado.
        Usa 13 atributos base + Armor para calcular stats derivados.
        
        Atributos Base:
        - Força, Destreza, Velocidade
        - Resistência, Constituição
        - Inteligência, Sabedoria
        - Poder, Foco, Sentidos
        - Vontade, Instinto, Espírito
        - Armor (calculado de itens)
        
        Stats Derivados (Fórmulas):
        - HP: Constituição
        - MP: Foco
        - SP: ((Destreza + Velocidade)/2)+1
        - Defesa: Armor + Resistência
        - Esquiva: Defesa + Destreza
        - Bloqueio: Defesa + Constituição
        - Contra-Ataque: Defesa - Destreza
        """
        # Inicializa com 0 todos os atributos base
        stats = {
            # Atributos Base (somam dos itens)
            'forca': 0,              # Força
            'destreza': 0,           # Destreza
            'velocidade': 0,         # Velocidade
            'resistencia': 0,        # Resistência
            'constituicao': 0,       # Constituição
            'inteligencia': 0,       # Inteligência
            'sabedoria': 0,          # Sabedoria
            'poder': 0,              # Poder
            'foco': 0,               # Foco
            'sentidos': 0,           # Sentidos
            'vontade': 0,            # Vontade
            'instinto': 0,           # Instinto
            'espirito': 0,           # Espírito
            'armor': 0,              # Armadura (total)
        }
        
        # Soma stats de todos os itens equipados
        for slot in EquipSlot.query.all():
            item = slot.get_equipped_item()
            if item:
                item_stats = item.get_stats()
                for key, value in item_stats.items():
                    if key in stats and isinstance(value, (int, float)):
                        stats[key] += value
        
        # Calcula stats derivados usando as fórmulas
        stats['hp'] = stats['constituicao']
        stats['mp'] = stats['foco']
        stats['sp'] = int(((stats['destreza'] + stats['velocidade']) / 2) + 1)
        stats['defesa'] = stats['armor'] + stats['resistencia']
        stats['esquiva'] = stats['defesa'] + stats['destreza']
        stats['bloqueio'] = stats['defesa'] + stats['constituicao']
        stats['contra_ataque'] = stats['defesa'] - stats['destreza']
        
        # Garante que valores sejam positivos
        stats['hp'] = max(1, stats['hp'])
        stats['mp'] = max(0, stats['mp'])
        stats['sp'] = max(1, stats['sp'])
        stats['defesa'] = max(0, stats['defesa'])
        stats['esquiva'] = max(0, stats['esquiva'])
        stats['bloqueio'] = max(0, stats['bloqueio'])
        stats['contra_ataque'] = max(0, stats['contra_ataque'])
        
        return stats
    
    @staticmethod
    def get_equipment_summary(player):
        """
        Retorna resumo do set equipado formatado para exibição.
        """
        summary = {
            'equipped_items': [],
            'total_stats': {},
            'empty_slots': 0,
            'locked_slots': 0,
        }
        
        # Coleta itens equipados
        for slot in EquipSlot.query.all():
            item = slot.get_equipped_item()
            if item:
                summary['equipped_items'].append({
                    'slot_name': slot.name,
                    'item_name': item.name,
                    'rarity': item.rarity,
                    'stats': item.get_stats(),
                })
            else:
                summary['empty_slots'] += 1
            
            if slot.is_locked:
                summary['locked_slots'] += 1
        
        # Calcula stats totais
        summary['total_stats'] = CalculationService.calculate_player_stats(player)
        
        return summary
    
    @staticmethod
    def format_stat_display(stats):
        """
        Formata stats para exibição amigável.
        Mostra atributos base e stats derivados.
        """
        formatted = {
            'atributos_base': [],
            'stats_derivados': []
        }
        
        # Labels para atributos base
        atributos_labels = {
            'forca': ('Força', 'red'),
            'destreza': ('Destreza', 'yellow'),
            'velocidade': ('Velocidade', 'cyan'),
            'resistencia': ('Resistência', 'green'),
            'constituicao': ('Constituição', 'orange'),
            'inteligencia': ('Inteligência', 'blue'),
            'sabedoria': ('Sabedoria', 'purple'),
            'poder': ('Poder', 'magenta'),
            'foco': ('Foco', 'lime'),
            'sentidos': ('Sentidos', 'pink'),
            'vontade': ('Vontade', 'teal'),
            'instinto': ('Instinto', 'brown'),
            'espirito': ('Espírito', 'silver'),
        }
        
        # Labels para stats derivados
        stats_labels = {
            'armor': ('Armadura', 'gray'),
            'hp': ('Vida', 'red'),
            'mp': ('Mana', 'blue'),
            'sp': ('Stamina', 'yellow'),
            'defesa': ('Defesa', 'green'),
            'esquiva': ('Esquiva', 'cyan'),
            'bloqueio': ('Bloqueio', 'orange'),
            'contra_ataque': ('Contra-Ataque', 'purple'),
        }
        
        # Processa atributos base
        for key, (label, color) in atributos_labels.items():
            if key in stats:
                value = stats[key]
                formatted['atributos_base'].append({
                    'label': label,
                    'value': int(value),
                    'color': color,
                    'is_positive': value > 0,
                })
        
        # Processa stats derivados
        for key, (label, color) in stats_labels.items():
            if key in stats:
                value = stats[key]
                formatted['stats_derivados'].append({
                    'label': label,
                    'value': int(value),
                    'color': color,
                    'is_positive': value > 0,
                })
        
        return formatted
