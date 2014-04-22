#############################
# License : https://www.gnu.org/licenses/lgpl.html  LGPL V3
# Author: Morris Winkler m.winkler@open3dengineering.org
#
# This is a plugin to generate a Bill of Materials 
# for Open Hardware Projects. Use as is, please notify  
# me about any enhacements you make to this code.

from __future__ import with_statement
import contextlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import sys

import csv
import collections
import bpy
from bpy.props import *
from bpy.types import PropertyGroup


#############################
# globals

_objects = bpy.data.objects


#############################
# helper functions

# create tiny url
def make_tinyurl(url):
    request_url = ('http://tinyurl.com/api-create.php?' + 
    urlencode({'url':url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8')

# get sections
def get_sections(self, context):
    sects = []
    ret = []
    for ob in _objects:
        sects.append(ob.bom_section)
    uniq_sects = set(sects)
    for i, uniq in enumerate(uniq_sects):
        ret.append((uniq, uniq, 'none', i))
        
    return(ret)       
        
# set sections
def update_sections(self, context):
    name = context.object.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_section != context.scene.bom.sections:
                ob.bom_section = context.scene.bom.sections

# get descriptions
def get_descs(self, context):
    descs = []
    ret = []
    for ob in _objects:
        descs.append(ob.bom_desc)
    uniq_descs = set(descs)
    for i, uniq in enumerate(uniq_descs):
        ret.append((uniq, uniq, 'none', i))
        
    return(ret)       
        
# set descriptions
def update_descs(self, context):
    name = context.object.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_desc != context.scene.bom.descs:
                ob.bom_desc = context.scene.bom.descs

# get reseller
def get_resellers(self, context):
    resellers = []
    ret = []
    for ob in _objects:
        resellers.append(ob.bom_reseller)
    uniq_resellers = set(resellers)
    for i, uniq in enumerate(uniq_resellers):
        ret.append((uniq, uniq, 'none', i))

    return(ret)       
        
# set resellers
def update_resellers(self, context):
    name = context.object.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_reseller != context.scene.bom.resellers:
                ob.bom_reseller = context.scene.bom.resellers

# export the bom to csv file    
def write_bom(self, context):
    bom = bpy.context.scene.bom
    objects = collections.defaultdict(lambda: collections.defaultdict(dict))
    
    fields = ['Section', 'Part', 'QTY', 'Description', 'Reseller', 'Product URL', 'Unit Price', 'Total']
                
    # get sections and fill them with objects and object values
    sections = get_sections(self, context)
    scene = context.scene
    for sect in sections:
        if sect[1] != 'nosection':
            for ob in scene.objects:
                name = ob.name.split('.')[0]
                print(ob.users_scene)
                if ob.type == 'MESH' and ob.bom_section == sect[1]:
       
                    objects[sect[1]][name]['Section'] = sect[1]
                    objects[sect[1]][name]['Part'] = name 
                    try:
                        objects[sect[1]][name]['QTY'] += 1
                    except:
                        objects[sect[1]][name]['QTY'] = 1
                    objects[sect[1]][name]['Description'] = bpy.data.objects[name].bom_desc
                    objects[sect[1]][name]['Reseller'] = bpy.data.objects[name].bom_reseller
                    objects[sect[1]][name]['Product URL'] = bpy.data.objects[name].bom_product_url
                    #print(make_tinyurl(bpy.data.objects[name].bom_product_url))
                    objects[sect[1]][name]['Unit Price'] = round(bpy.data.objects[name].bom_price, 2)
                    total = objects[sect[1]][name]['Unit Price'] * objects[sect[1]][name]['QTY']
                    objects[sect[1]][name]['Total'] = round(total,2)
                
                             

    # write csv file with 8 collumns
    total = 0.0
    ofile = bom.export_file
    fw = open(ofile, 'w')
    
    writer = csv.writer(fw)
    writer.writerow(fields)
    for sect in sorted(objects.keys()):
        if sect != 'nosection':
            sub_total = 0.0
            for ob in sorted(objects[sect].keys()):
                row = []
                for field in fields:
                    if field == 'Product URL':
                        tinyurl = make_tinyurl(objects[sect][ob][field])
                        if tinyurl == 'Error':
                            row.append(str(objects[sect][ob][field]))    
                        else:        
                            row.append(tinyurl)
                    else:
                        row.append(str(objects[sect][ob][field])) 
                
                sub_total += objects[sect][ob]['Total']
                writer.writerow(row)
            
            total += sub_total        
            writer.writerow(['', '', '', '', '', '', 'Sub Total', round(sub_total, 2)])    
    
    # nosection is blacklisted for now
    #sub_total = 0.0
    #for ob in sorted(objects['nosection'].keys()):
    #    row = []
    #    for field in fields:
    #        row.append(str(objects['nosection'][ob][field])) 
    #                
    #    sub_total += objects['nosection'][ob]['Total']
    #    writer.writerow(row)    
    #
    #total += sub_total
    #writer.writerow(['', '', '', '', '', '', 'Sub Total', round(sub_total, 2)])        
    writer.writerow(['', '', '', '', '', '', 'Total', round(total, 2)])

    fw.close
    return True   

#############################
# update function for RNA props    

# section
def update_equals_section(self, context):
    name = self.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_section != context.object.bom_section:
                ob.bom_section = context.object.bom_section 

# description
def update_equals_desc(self, context):
    name = self.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_desc != context.object.bom_desc:
                ob.bom_desc = context.object.bom_desc 

# price
def update_equals_price(self, context):
    name = self.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_price != context.object.bom_price:
                ob.bom_price = context.object.bom_price 

# reseller 
def update_equals_reseller(self, context):
    name = self.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_reseller != context.object.bom_reseller:
                ob.bom_reseller = context.object.bom_reseller            

# product url 
def update_equals_product_url(self, context):
    name = self.name.split('.')[0]
    for ob in _objects:
        if ob.type == 'MESH' and ob.name.split('.')[0] == name:
            if ob.bom_product_url != context.object.bom_product_url:
                ob.bom_product_url = context.object.bom_product_url            

#############################
# RNA properties for BOM

# bom settings
class BomSettings(PropertyGroup):
    export_file = StringProperty(
        name="Export File",
        description="File to export the BOM to",
        default="BOM.csv", 
        maxlen=1024, 
        subtype="FILE_PATH")
    
    descs = EnumProperty(
        name = 'Descriptions',
        description = 'BOM Descriptions',
        items = get_descs,
        update = update_descs)    
        
    sections = EnumProperty(
        name = 'Sections',
        description = 'BOM Sections',
        items = get_sections,
        update = update_sections)
    
    resellers = EnumProperty(
        name = 'Resellers',
        description = 'BOM Resellers',
        items = get_resellers,
        update = update_resellers)       

# object properties
bpy.types.Object.bom_section = StringProperty(
    name = "Section", 
    default = "nosection",
    update = update_equals_section)

bpy.types.Object.bom_desc = StringProperty(
    name = "Description", 
    default = "none",
    update = update_equals_desc)

bpy.types.Object.bom_price = FloatProperty(
    name = "Price", 
    update = update_equals_price,
    precision = 2)

bpy.types.Object.bom_reseller = StringProperty(
    name = "Reseller", 
    default = "none",
    update = update_equals_reseller)
    
bpy.types.Object.bom_product_url = StringProperty(
    name = "Product URL", 
    default = "none",
    update = update_equals_product_url)    
#############################
# Operators 
    
class OBJECT_OT_ExportButton(bpy.types.Operator):
    bl_idname = "bom.export"
    bl_label = "Export CSV"
     
    def execute(self, context):
        ret = write_bom(self, context)
        if ret:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}    
        
                
        
#############################
# custom UI in Properties->Object Panel    
class ObjectPanel(bpy.types.Panel):
    bl_label = "Bom Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        ob = context.object
        bom = context.scene.bom
        
        if not ob:
            return
        layout = self.layout
 
        
        col = layout.column_flow(align=True)
        col.label('Section:')
        row = col.row(align=True)    
        row.prop_menu_enum(bom, 'sections', text='', icon='TRIA_DOWN')
        row.prop(ob, 'bom_section', text='')
        
        col = layout.column_flow(align=True)
        col.label('Description:')
        row = col.row(align=True)    
        row.prop_menu_enum(bom, 'descs', text='', icon='TRIA_DOWN')
        row.prop(ob, 'bom_desc', text='')
        
        layout.label('Price:')    
        layout.prop(ob, 'bom_price', text='')
        
        col = layout.column_flow(align=True)
        col.label('Reseller:')
        row = col.row(align=True) 
        row.prop_menu_enum(bom, 'resellers', text='', icon='TRIA_DOWN')    
        row.prop(ob, 'bom_reseller', text='')            
        
        layout.label('Product URL:')    
        layout.prop(ob, 'bom_product_url', text='')
        
        layout.separator()
        layout.prop(bom,  "export_file", text="")
        layout.operator("bom.export", text='Export')
        # should we go safe ??
        #try:
        #    ob['bom_section']
        #    layout.prop(ob, 'bom_section')
        #except:
        #    pass
 
# Registration
bpy.utils.register_module(__name__) 
bpy.types.Scene.bom = PointerProperty(type=BomSettings) 
