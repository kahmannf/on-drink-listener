import json, os, inspect

class Data:

    application_name = ''

    view_name = 'Cocktail Mixer!'

    recipes = []
    beverages = []
    supply = []

    server_config = None

    def __init__(self, server_config):
        self.server_config = server_config
        self.application_name = server_config['app_name'] 
        self.beverages = sorted(load_from_file(server_config['beverages_dir']), key= lambda bev : bev.get('name'))
        self.supply = sorted(load_from_file(server_config['supply_dir']), key= lambda sup : sup.get('slot'))
        self.recipes = sorted(load_from_file(server_config['recipes_dir']), key= lambda rec : rec.get('name'))
        
    def get_supply_item(self, name):
        for supply_item in self.supply:
            if supply_item['beverage'].lower() == name.lower():
                return supply_item
        return None

    def get_beverage(self, name):
        for beverage in self.beverages:
            if beverage['name'].lower() == name.lower():
                return beverage
        return None

    def get_recipe(self, name):
        for recipe in self.recipes:
            if recipe['name'].lower() == name.lower():
                return recipe
        return None

    def can_mix(self, recipe):
        totalML = int(self.server_config['glass_size'])
        
        total_parts = 0
        for ingredient in recipe['ingredients']:
            total_parts += int(ingredient['amount'])
        
        for ingredient in recipe['ingredients']:
            supply_item = self.get_supply_item(name=ingredient['beverage'])
            if supply_item:
                required_amount = float(totalML) * float(ingredient['amount']) / float(total_parts) 
                if required_amount > int(supply_item['amount']):
                    return False
            else:
                return False
        return True


    def filter_recipes(self):
        available_recipes = []
        for recipe in self.recipes:
            if self.can_mix(recipe=recipe):
                available_recipes.append(recipe)
        self.recipes = available_recipes

    def set_supply_item(self, supply_item):
        for sup in self.supply:
            if sup['slot'] == supply_item['slot']:
                self.supply[self.supply.index(sup)] = supply_item

        if not supply_item in self.supply:
            self.supply.append(supply_item)
        
        server_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        supply_dir = os.path.join(server_dir, self.server_config['supply_dir'])

        filename = os.path.join(supply_dir, 'slot%s.json' % str(supply_item['slot']))

        save_to_file(filename, supply_item)

    def update_or_create_beverage(self, beverage, old_name):
        original_beverage = self.get_beverage(name=old_name)

        server_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        supply_dir = os.path.join(server_dir, self.server_config['beverages_dir'])

        if original_beverage:
            self.beverages[self.beverages.index(original_beverage)] = beverage
            old_filename = os.path.join(supply_dir, '%s.json' % old_name.replace(' ', '').lower())
            os.remove(old_filename)
        else:
            self.beverages.append(beverage)
        
        filename = os.path.join(supply_dir, '%s.json' % beverage['name'].replace(' ', '').lower())

        save_to_file(filename, beverage)

    def update_or_create_recipe(self, recipe, old_name):
        
        original_recipe = None
        if old_name:
            original_recipe = self.get_recipe(name=old_name)

        server_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        recipes_dir = os.path.join(server_dir, self.server_config['recipes_dir'])

        if original_recipe:
            self.recipes[self.recipes.index(original_recipe)] = recipe
            old_filename = os.path.join(recipes_dir, '%s.json' % old_name.replace(' ', '').lower())
            os.remove(old_filename)
        else:
            self.beverages.append(recipe)
        
        filename = os.path.join(recipes_dir, '%s.json' % recipe['name'].replace(' ', '').lower())

        save_to_file(filename, recipe)

    def remove_amount(self, beverage_name, amount_ml):
        supply_item = self.get_supply_item(beverage_name)
        supply_item['amount'] -= amount_ml
        self.set_supply_item(supply_item)

def get_file_names(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def load_from_file(dir):
    result_list = []
    
    server_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    source_dir = os.path.join(server_dir, dir)
    
    if not os.path.isdir(source_dir):
        return result_list
    
    files = get_file_names(source_dir)

    for filename in files:
        full_filename = os.path.join(source_dir, filename)

        with open(full_filename, 'rU') as file_stream:
            dictionary = json.load(file_stream)

            result_list.append(dictionary)
    
    return result_list

def save_to_file(filename, dict_obj):
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, 'w') as file_stream:
        json.dump(dict_obj, file_stream, indent=4)

