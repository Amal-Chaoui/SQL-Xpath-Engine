import load
import query

if __name__ == '__main__':
    load.load('test.xml')
    def run(xpath_str):
        return query.query(xpath_str)
    # simple step
    assert run('/child::a') == {1, 7, 13}

    # joins
    assert run('/child::a/child::b') == {5, 8, 15}
    assert run('/child::a/child::b/child::c') ==  {9}

    # axes
    
    #print(run('/child::a/descendant::a'))
    assert run('/child::a/descendant::a') == {3, 10, 14}
    assert run('/child::a/descendant-or-self::a') == {1, 3, 7, 10, 13, 14}
    
    assert run('/child::a/child::b/parent::a') == {1, 7, 13}
    assert run('/child::a/child::a/ancestor::a') == {1, 13}
    assert run('/child::a/child::a/ancestor-or-self::a') == {1, 3, 13, 14}
    assert run('/self::root') == {0}
    assert run('/child::a/self::a') == {1, 7, 13}
    
    assert run('/child::a/child::x/following-sibling::*') == {3, 4, 5, 6}
    assert run('/child::a/child::y/following-sibling::*') == {5, 6}
    assert run('/child::a/child::z/following-sibling::*') == set()
    assert run('/child::a/child::x/preceding-sibling::*') == set()
    assert run('/child::a/child::y/preceding-sibling::*') == {2, 3}
    assert run('/child::a/child::z/preceding-sibling::*') == {2, 3, 4, 5}


    # star node selection

    assert run('/child::a/child::*') == {2, 3, 4, 5, 6, 8, 14, 15}

    # filter expressions
    assert run('/child::a[child::a]') == {1, 13}
    assert run('/child::a[child::a and child::b]') == {1, 13}
        
