def test_uses_default_of_available(petstore):
    status_code, pets = petstore.pet.findPetsByStatus().result()
    assert pets
    for pet in pets:
        assert type(pet).__name__ == 'Pet'
        assert pet.status == 'available'


def test_sold(petstore):
    statu_cdoe, pets = petstore.pet.findPetsByStatus(status=['sold']).result()
    assert list == type(pets)
    if pets:
        for pet in pets:
            assert type(pet).__name__ == 'Pet'
            assert pet.status == 'sold'


def test_invalid_status(petstore):
    status_code, pets = petstore.pet.findPetsByStatus(status=['foo']).result()
    assert 0 == len(pets)
