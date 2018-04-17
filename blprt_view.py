from flask import Blueprint, render_template, abort, request, flash, redirect, session, url_for
from configuration import get_config
from data import Data
from controller import Controller


view_blueprint = Blueprint('view_blueprint', __name__, template_folder='templates')

config = get_config()

controller = Controller()

@view_blueprint.route('/', methods=['GET'])
def show_recipes():
    data = Data(server_config=config)
    
    data.view_name = 'Menu'

    return render_template('show_recipes.html', data=data)

@view_blueprint.route('/filtered/', methods=['GET'])
def show_recipes_filtered():
    data = Data(server_config=config)

    data.view_name = 'Available recipes'

    data.filter_recipes()

    return render_template('show_recipes.html', data=data)

@view_blueprint.route('/maintenance/', methods=['GET', 'POST'])
def maintenance():
    data = Data(server_config=config)
    data.view_name = 'Maintenance'

    if request.method == 'POST':
        if not session.get('logged_in', False):
            if config.get('maintenance_pin', '0') == '0':
            
                flash('Server-side issue: No pin configured')
                return render_template('maintenance_login.html', data=data)
            
            elif request.form['pin'] != config['maintenance_pin']:
            
                flash('Invalid pin!')
                return render_template('maintenance_login.html', data=data)
            
            else:
            
                session['logged_in'] = True
                return redirect(url_for('view_blueprint.maintenance'))
        else: ##code for logout
            session['logged_in'] = False
            return redirect(url_for('view_blueprint.show_recipes'))
    else:
        print(session.get('logged_in', False))
        if session.get('logged_in', False):
    	    return render_template('ma_supply.html', data=data)
        else:
    	    return render_template('maintenance_login.html', data=data)

@view_blueprint.route('/set_slot/', methods=['GET','POST'])
def set_slot():
    data = Data(server_config=config)

    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))

    if request.method == 'POST':
        slot =int(request.form.get('slot', -1))
        beverage_name = request.form.get('beverage', None)
        amount = int(request.form.get('amount', 0))

        error_messages = []

        if slot < 0:
            error_messages.append('Invalid slot number: %s' % slot)
        
        if amount < 0:
            error_messages.append('Invalid amount: %s' % amount)
        
        beverage = data.get_beverage(beverage_name)

        if not beverage:
            error_messages.append('Unknown beverage: %s' % beverage_name)

        if len(error_messages) > 0:
            for message in error_messages:
                flash(message)
        else:
            supply_item = {
                'slot': slot,
                'beverage': beverage['name'],
                'amount': amount
            }
            data.set_supply_item(supply_item)

        return redirect(url_for('view_blueprint.maintenance'))

    data.view_name = 'Set slot data'

    slot = int(request.args.get('slot', -1))

    if  slot == -1:
        return redirect(url_for('view_blueprint.show_recipes'))
    else:
        return render_template('set_slot.html', data=data, slot=str(slot))

@view_blueprint.route('/clear_slot/', methods=['GET','POST'])
def clear_slot():
    data = Data(server_config=config)

    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))

    if request.method == 'GET':
        slot = int(request.args.get('slot', -1))
        

        error_messages = []

        if slot < 0:
            error_messages.append('Invalid slot number: %s' % slot)
        if len(error_messages) > 0:
            for message in error_messages:
                flash(message)
        else:
            data.clear_supply_item(slot)

    return redirect(url_for('view_blueprint.maintenance'))


@view_blueprint.route('/maintenance/beverages/', methods=['GET'])
def ma_beverages():
    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))

    data = Data(server_config=config)

    data.view_name = 'Beverages'

    return render_template('ma_beverages.html', data=data)

@view_blueprint.route('/edit_beverage/', methods=['GET', 'POST'])
def edit_beverage():
    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))

    data = Data(server_config=config)

    if request.method == 'POST':
        name = request.form.get('name', '')
        viscosity = int(request.form.get('viscosity', -1))
        alcohol_vol = int(request.form.get('alcohol_vol', -1))
        old_name = request.form.get('old_name', '')

        error_messages = []

        check_name_beverage = data.get_beverage(old_name)

        if not name:
            error_messages.append('Name cannot be empty')
        
        if viscosity < 0:
            error_messages.append('Invalid value for viscosity')

        if alcohol_vol < 0:
            error_messages.append('Invalid value for Alcohol Vol. Percentage')

        if old_name and old_name != name and check_name_beverage:
            error_messages.append('A beverage with the name "%s" already exists' % name)

        if len(error_messages) > 0:
            for message in error_messages:
                flash(message)
        else:
            data.update_or_create_beverage({
                'name': name,
                'viscosity': viscosity,
                'alcohol_vol': alcohol_vol
            }, old_name=old_name)


        return redirect(url_for('view_blueprint.ma_beverages'))

    beverage_name = request.args.get('name', '')
    
    beverage = data.get_beverage(beverage_name)

    if not beverage_name or not beverage:
        flash('Unknown beverage: %s' % beverage_name)
        return redirect(url_for('view_blueprint.ma_beverages'))
    else:
        data.view_name = 'Edit beverage: %s' % beverage['name']
        return render_template('edit_beverage.html', data=data, beverage=beverage, old_name=beverage_name)

@view_blueprint.route('/new_beverage/', methods=['GET'])
def new_beverage():
    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))

    data = Data(server_config=config)

    data.view_name = 'Create new Beverage'

    return render_template('edit_beverage.html', data=data, beverage={})

@view_blueprint.route('/ma_recipes/', methods=['GET'])
def ma_recipes():
    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))
    
    data = Data(server_config=config)

    data.view_name = 'Recipes'

    return render_template('ma_recipes.html', data=data)

@view_blueprint.route('/new_recipe/', methods=['GET'])
def new_recipe():
    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))
    
    data = Data(server_config=config)

    recipe_dummy = {
        'name' : '',
        'ingredients' : [ {
            'beverage' : data.beverages[0]['name'],
            'amount' : 0
        }]
    }

    data.view_name = 'Create new recipe'
    return render_template('edit_recipe.html', data=data, recipe=recipe_dummy, len=len)

@view_blueprint.route('/edit_recipe/', methods=['GET', 'POST'])
def edit_recipe():
    if not session.get('logged_in', False):
        return redirect(url_for('view_blueprint.maintenance'))
    
    data = Data(server_config=config)

    if request.method == 'POST':
        old_name = request.form.get('old_name', None)
        name = request.form.get('name', None)

        total_ingredients = int(request.form.get('total_ingredients', 0))

        if total_ingredients < 1:
            flash('A recipe has to have at least one ingredient')
            return redirect(url_for('view_blueprint.ma_recipes'))
        
        current_ingredient_index = 0
        parsed_ingredients = []

        error_messages = []

        while len(parsed_ingredients) < total_ingredients and current_ingredient_index < 100: ## we just assume that nobody is crazy enogh to create a cocktail with more that 100 igredients. would not fit into the glass anyways
            beverage_input = 'beverage%s' % current_ingredient_index
            amount_input = 'amount%s' % current_ingredient_index
            
            beverage_name = request.form.get(beverage_input, None)
            if not beverage_name:
                continue

            beverage = data.get_beverage(beverage_name)

            if not beverage:
                error_messages.append('Unknown beverage: %s' % beverage_name)
                break

            amount = int(request.form.get(amount_input, 0))

            if amount < 1:
                error_messages.append('Amount for %s is invalid' % beverage['name'])
                break

            parsed_ingredients.append({
                'beverage' : beverage['name'],
                'amount' : amount
            })

            current_ingredient_index += 1

        if len(parsed_ingredients) < total_ingredients:
            error_messages.append('Failed toparse ingredients')
        
        check_name_recipe = data.get_recipe(name)

        if old_name and old_name != name and check_name_recipe:
            error_messages.append('A recipe with the name "%s" already exists' % name)

        if len(error_messages) > 0:
            for message in error_messages:
                flash(message)
        else:
            data.update_or_create_recipe({
                'name': name,
                'ingredients' : parsed_ingredients
            }, old_name=old_name)


        return redirect(url_for('view_blueprint.ma_recipes'))
        

    recipe_name = request.args.get('name', '')
    
    recipe = data.get_recipe(recipe_name)

    if not recipe_name or not recipe:
        flash('Unknown recipe: %s' % recipe_name)
        return redirect(url_for('view_blueprint.ma_recipes'))
    else:
        data.view_name = 'Edit recipe: %s' % recipe['name']
        return render_template('edit_recipe.html', data=data, recipe=recipe, old_name=recipe_name, len=len)

@view_blueprint.route('/mix/')
def mix():
    data = Data(server_config=config)
    
    error_messages = []
    
    recipe_name = request.args.get('name', '')

    if not recipe_name or recipe_name == '':
        error_messages.append('No recipe name in request url')

    recipe = data.get_recipe(recipe_name)

    if not recipe:
        error_messages.append('No recipe with name "%s"' % recipe_name)

    if recipe and not data.can_mix(recipe):
        error_messages.append('Not enough ingredients for "%s"' % recipe_name)

    if not controller.isAvailable:
        error_messages.append('Already mixing Cocktail')

    if len(error_messages) > 0:
        for message in error_messages:
            flash(message)
    else:
        controller.mix_cocktail(recipe, config)
        flash('Mixing Cocktail "%s"' % recipe['name'])

    return redirect(url_for('view_blueprint.show_recipes'))


