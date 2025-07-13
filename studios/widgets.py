from django.forms import widgets
from django.utils.safestring import mark_safe
import json


class EquipmentWidget(widgets.Widget):
    template_name = 'widgets/equipment_widget.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Парсим текущее значение оборудования
        equipment_list = []
        if value:
            try:
                equipment_dict = json.loads(value)
                for item, quantity in equipment_dict.items():
                    equipment_list.append({'name': item, 'quantity': quantity})
            except json.JSONDecodeError:
                pass

        # Если нет оборудования, добавляем пустую строку
        if not equipment_list:
            equipment_list.append({'name': '', 'quantity': ''})

        context['widget']['equipment_list'] = equipment_list
        return context

    def value_from_datadict(self, data, files, name):
        # Собираем данные из динамических полей
        names = data.getlist(f'{name}_name')
        quantities = data.getlist(f'{name}_quantity')

        # Формируем JSON словарь
        equipment_dict = {}
        for i in range(len(names)):
            name_val = names[i].strip()
            quantity_val = quantities[i].strip()

            if name_val and quantity_val:
                try:
                    equipment_dict[name_val] = int(quantity_val)
                except ValueError:
                    pass

        return json.dumps(equipment_dict)