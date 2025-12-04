from typing import TypedDict, Annotated, List, Tuple
import re


class CostoLineaLineaMejor(TypedDict):
    lineas: Annotated[list[str], "Lista de líneas de código"]
    costos: Annotated[list[str], "Lista de costos asociados a cada línea"]


class CostoLineaLineaPeor(TypedDict):
    lineas: Annotated[list[str], "Lista de líneas de código"]
    costos: Annotated[list[str], "Lista de costos asociados a cada línea"]


class AnalizadorCostoLineas:
    """Analiza el código línea por línea y genera sumatorias de costo"""
    
    def __init__(self):
        self.lineas_codigo = []
        self.costos_mejor_caso = []
        self.costos_peor_caso = []
        self.contexto_actual = []  # Stack de contextos (for, while, if)
        
    def _es_declaracion_funcion(self, line: str) -> bool:
        """Detecta si una línea es una declaración de función"""
        # Una declaración de función tiene paréntesis y no es una llamada ni estructura de control
        if '(' not in line or ')' not in line:
            return False
        if any(keyword in line.lower() for keyword in ['call', 'if', 'while', 'for', '🡨', '<-']):
            return False
        return True
    
    def analizar_pseudocodigo(self, pseudocode: str) -> Tuple[CostoLineaLineaMejor, CostoLineaLineaPeor]:
        """
        Analiza el pseudocódigo línea por línea y genera los costos.
        
        Retorna:
            Tuple con (mejor_caso, peor_caso)
        """
        self.lineas_codigo = []
        self.costos_mejor_caso = []
        self.costos_peor_caso = []
        self.contexto_actual = []
        
        lines = pseudocode.strip().split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Ignorar líneas vacías
            if not line_stripped:
                continue
                
            # Ignorar comentarios
            if line_stripped.startswith('►'):
                continue
            
            line_lower = line_stripped.lower()
            
            # Ignorar declaraciones de función
            if self._es_declaracion_funcion(line_stripped):
                continue
            
            # Detectar inicio de estructuras de control
            if line_lower.startswith('for'):
                self._procesar_linea_for(line_stripped, add_as_line=True)
            elif line_lower.startswith('while'):
                self._procesar_linea_while(line_stripped, add_as_line=True)
            elif line_lower.startswith('if'):
                self._procesar_linea_if(line_stripped)
            elif line_lower == 'begin':
                # El begin no cuenta como línea ejecutable
                continue
            elif line_lower == 'end':
                # Cerrar el contexto actual
                if self.contexto_actual:
                    self.contexto_actual.pop()
                continue
            elif line_lower.startswith('else'):
                # Cambiar el contexto de if a else
                if self.contexto_actual and self.contexto_actual[-1][0] == 'if':
                    # Mantener el mismo nivel pero marcar como else
                    contexto = self.contexto_actual[-1]
                    self.contexto_actual[-1] = ('else', contexto[1])
                continue
            else:
                # Línea de código ejecutable
                self._procesar_linea_ejecutable(line_stripped)
        
        mejor_caso: CostoLineaLineaMejor = {
            'lineas': self.lineas_codigo,
            'costos': self.costos_mejor_caso
        }
        
        peor_caso: CostoLineaLineaPeor = {
            'lineas': self.lineas_codigo,
            'costos': self.costos_peor_caso
        }
        
        return mejor_caso, peor_caso
    
    def _procesar_linea_for(self, line: str, add_as_line: bool = False):
        """Procesa una línea for y añade el contexto"""
        # Extraer el límite: for i <- 1 to n do
        # Captura todo desde 'to' hasta 'do' (excluyendo 'do')
        match = re.search(r'to\s+(.+?)\s+do', line, re.IGNORECASE)
        if match:
            limite = match.group(1).strip()
            
            # Si se requiere, agregar la línea del for como ejecutable
            if add_as_line:
                self._agregar_linea_ciclo_for(line, limite)
            
            # Agregar el contexto DESPUÉS de calcular el costo de la línea
            self.contexto_actual.append(('for', limite))
    
    def _procesar_linea_while(self, line: str, add_as_line: bool = False):
        """Procesa una línea while y añade el contexto"""
        # Extraer la condición: while (condicion) do
        match = re.search(r'while\s+\(?([^)]+)\)?', line, re.IGNORECASE)
        if match:
            condicion = match.group(1).strip().replace('do', '').replace(')', '').strip()
            
            # Si se requiere, agregar la línea del while como ejecutable
            if add_as_line:
                self._agregar_linea_ciclo_while(line, condicion)
            
            # Agregar el contexto DESPUÉS de calcular el costo de la línea
            self.contexto_actual.append(('while', condicion))
    
    def _procesar_linea_if(self, line: str):
        """Procesa una línea if y añade el contexto"""
        # Extraer la condición: if (condicion) then
        match = re.search(r'if\s+\(?([^)]+)\)?', line, re.IGNORECASE)
        if match:
            condicion = match.group(1).strip().replace('then', '').replace(')', '').strip()
            self.contexto_actual.append(('if', condicion))
    
    def _agregar_linea_ciclo_for(self, line: str, limite: str):
        """Agrega la línea del for como línea ejecutable con su costo"""
        self.lineas_codigo.append(line)
        
        # El costo del FOR es: (limite)+1 evaluaciones de la condición (en el contexto actual)
        # Antes de estar dentro del for
        costo_base_mejor = self._generar_sumatoria_mejor() if self.contexto_actual else "1"
        costo_base_peor = self._generar_sumatoria_peor() if self.contexto_actual else "1"
        
        # El for evalúa la condición (limite)+1 veces
        # Si el límite tiene operaciones, lo envolvemos en paréntesis
        limite_formateado = f"({limite})" if any(op in limite for op in ['+', '-', '*', '/', ' ']) else limite
        
        if costo_base_mejor == "1":
            costo_mejor = f"{limite_formateado} + 1"
        else:
            costo_mejor = f"({limite_formateado} + 1) * {costo_base_mejor}"
            
        if costo_base_peor == "1":
            costo_peor = f"{limite_formateado} + 1"
        else:
            costo_peor = f"({limite_formateado} + 1) * {costo_base_peor}"
        
        self.costos_mejor_caso.append(costo_mejor)
        self.costos_peor_caso.append(costo_peor)
    
    def _agregar_linea_ciclo_while(self, line: str, condicion: str):
        """Agrega la línea del while como línea ejecutable con su costo"""
        self.lineas_codigo.append(line)
        
        # El costo del WHILE depende del contexto actual
        costo_base_mejor = self._generar_sumatoria_mejor() if self.contexto_actual else "1"
        costo_base_peor = self._generar_sumatoria_peor() if self.contexto_actual else "1"
        
        # El while evalúa la condición W+1 veces (W iteraciones + 1 cuando falla)
        if costo_base_mejor == "1":
            costo_mejor = f"W_{{{condicion}}} + 1"
        else:
            costo_mejor = f"(W_{{{condicion}}} + 1) * {costo_base_mejor}"
            
        if costo_base_peor == "1":
            costo_peor = f"W_{{{condicion}}} + 1"
        else:
            costo_peor = f"(W_{{{condicion}}} + 1) * {costo_base_peor}"
        
        self.costos_mejor_caso.append(costo_mejor)
        self.costos_peor_caso.append(costo_peor)
    
    def _procesar_linea_ejecutable(self, line: str):
        """Procesa una línea ejecutable y calcula su costo"""
        self.lineas_codigo.append(line)
        
        # Calcular el costo basado en el contexto actual
        costo_mejor = self._generar_sumatoria_mejor()
        costo_peor = self._generar_sumatoria_peor()
        
        self.costos_mejor_caso.append(costo_mejor)
        self.costos_peor_caso.append(costo_peor)
    
    def _generar_sumatoria_mejor(self) -> str:
        """Genera la sumatoria para el mejor caso"""
        if not self.contexto_actual:
            return "1"
        
        # Construir la sumatoria desde el contexto más externo al más interno
        resultado = "1"
        indices = ['i', 'j', 'k', 'l', 'm']  # Índices para niveles anidados
        
        for idx, (tipo, valor) in enumerate(self.contexto_actual):
            indice = indices[idx % len(indices)]
            
            if tipo == 'for':
                resultado = f"sum({resultado}, {indice}, 1, {valor})"
            elif tipo == 'while':
                # En mejor caso, el while puede no ejecutarse o ejecutarse mínimamente
                resultado = f"W_{{{valor}}} * {resultado}"
            elif tipo == 'if':
                # En mejor caso, no entra en el if
                resultado = "0"
                break
            elif tipo == 'else':
                # En mejor caso, entra en el else (porque no entró en el if)
                # Mantener el resultado actual
                pass
        
        return resultado
    
    def _generar_sumatoria_peor(self) -> str:
        """Genera la sumatoria para el peor caso"""
        if not self.contexto_actual:
            return "1"
        
        # Construir la sumatoria desde el contexto más externo al más interno
        resultado = "1"
        indices = ['i', 'j', 'k', 'l', 'm']  # Índices para niveles anidados
        
        for idx, (tipo, valor) in enumerate(self.contexto_actual):
            indice = indices[idx % len(indices)]
            
            if tipo == 'for':
                resultado = f"sum({resultado}, {indice}, 1, {valor})"
            elif tipo == 'while':
                # En peor caso, el while se ejecuta el máximo de veces
                resultado = f"W_{{{valor}}} * {resultado}"
            elif tipo == 'if':
                # En peor caso, entra en el if
                # Mantener el resultado actual (se ejecuta)
                pass
            elif tipo == 'else':
                # En peor caso, no entra en el else (porque entró en el if)
                resultado = "0"
                break
        
        return resultado


def analizar_costo_lineas(pseudocode: str) -> Tuple[CostoLineaLineaMejor, CostoLineaLineaPeor]:
    """
    Función principal para analizar el costo línea por línea.
    
    Args:
        pseudocode: El pseudocódigo a analizar
        
    Returns:
        Tupla con (mejor_caso, peor_caso) conteniendo líneas y costos
    """
    analizador = AnalizadorCostoLineas()
    return analizador.analizar_pseudocodigo(pseudocode)