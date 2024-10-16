sim=require'sim'

function sysCall_init() 
    modelHandle=sim.getObject('.')
    randomColors=true
    HairColors={4,{0.30,0.22,0.14},{0.75,0.75,0.75},{0.075,0.075,0.075},{0.75,0.68,0.23}}
    skinColors={2,{0.91,0.84,0.75},{0.52,0.45,0.35}}
    --shirtColors={5,{0.37,0.46,0.74},{0.54,0.27,0.27},{0.31,0.51,0.33},{0.46,0.46,0.46},{0.18,0.18,0.18}}
    shirtColors={1,{1.0,0.0,0.0}}
    --trouserColors={2,{0.4,0.34,0.2},{0.12,0.12,0.12}}
    trouserColors={1,{1.0,0.0,0.0}}
    --shoeColors={2,{0.12,0.12,0.12},{0.25,0.12,0.045}}
    shoeColors={1,{1.0,0.0,0.0}}
    -- Initialize to random colors if desired:
    if (randomColors) then
        modelObjects=sim.getObjectsInTree(modelHandle)
        math.randomseed(sim.getFloatParam(sim.floatparam_rand)*10000) -- each lua instance should start with a different and 'good' seed
        setColor(modelObjects,'HAIR',HairColors[1+math.random(HairColors[1])])
        setColor(modelObjects,'SKIN',skinColors[1+math.random(skinColors[1])])
        setColor(modelObjects,'SHIRT',shirtColors[1+math.random(shirtColors[1])])
        setColor(modelObjects,'TROUSERS',trouserColors[1+math.random(trouserColors[1])])
        setColor(modelObjects,'SHOE',shoeColors[1+math.random(shoeColors[1])])
    end
end
 
setColor=function(objectTable,colorName,color)
    for i=1,#objectTable,1 do
        if (sim.getObjectType(objectTable[i])==sim.object_shape_type) then
            sim.setShapeColor(objectTable[i],colorName,0,color)
        end
    end
end


function sysCall_cleanup() 
    -- Restore to initial colors:
    if (randomColors) then
        local modelObjects=sim.getObjectsInTree(modelHandle)
        setColor(modelObjects,'HAIR',HairColors[2])
        setColor(modelObjects,'SKIN',skinColors[2])
        setColor(modelObjects,'SHIRT',shirtColors[2])
        setColor(modelObjects,'TROUSERS',trouserColors[2])
        setColor(modelObjects,'SHOE',shoeColors[2])
    end
end 
